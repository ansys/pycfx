# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module for events management."""

from functools import partial
import logging
from typing import Callable, List

from ansys.api.cfx.v0 import events_pb2 as EventsProtoModule
from ansys.cfx.core.exceptions import DisallowedValuesError, InvalidArgument
from ansys.cfx.core.streaming_services.streaming import StreamingService

event_logger = logging.getLogger("pycfx.server_event")


class EventsManager(StreamingService):
    """Manages server-side events.

    This class allows the client to register and unregister callbacks with server events.

    Parameters
    ----------
    session : BaseSession
        CFX session object.

    Attributes
    ----------
    events_list : List[str]
        List of supported events.
    """

    def __init__(self, session_events_service, cfx_error_state, session_id):
        """__init__ method of EventsManager class."""
        super().__init__(
            stream_begin_method="BeginStreaming",
            target=EventsManager._process_streaming,
            streaming_service=session_events_service,
        )
        self._cfx_error_state = cfx_error_state
        self._session_id: str = session_id
        self._events_list: List[str] = [
            attr for attr in dir(EventsProtoModule) if attr.endswith("Event")
        ]

    def _process_streaming(self, id, stream_begin_method, started_evt, *args, **kwargs):
        request = EventsProtoModule.BeginStreamingRequest(*args, **kwargs)
        responses = self._streaming_service.begin_streaming(
            request, started_evt, id=id, stream_begin_method=stream_begin_method
        )
        while True:
            try:
                response = next(responses)
                event_name = response.WhichOneof("as")
                with self._lock:
                    self._streaming = True
                    # CFX server error-code:
                    #   0 = server running without error
                    #   1 = warning/info messages
                    #   2 = std/internal errors
                    #   3 = fatal errors
                    if event_name == "errorevent" and response.errorevent.errorCode != 0:
                        error_message = response.errorevent.message.rstrip()
                        event_logger.error(
                            f"gRPC - {error_message}, " f"errorCode {response.errorevent.errorCode}"
                        )
                        if response.errorevent.errorCode > 2:
                            self._cfx_error_state.set("fatal", error_message)
                            continue
                    callbacks_map = self._service_callbacks.get(event_name, {})
                    for callback in callbacks_map.values():
                        callback(
                            session_id=self._session_id,
                            event_info=getattr(response, event_name),
                        )
            except StopIteration:
                break

    def register_callback(
        self,
        event_name: str,
        callback: Callable,
        *args,
        **kwargs,
    ):
        """Register the callback.

        Parameters
        ----------
        event_name : str
            Event name to register the callback to.
        callback : Callable
            Callback to register.
        args : Any
            Arguments.
        kwargs : Any
            Keyword arguments.

        Returns
        -------
        str
            Registered callback ID.

        Raises
        ------
        InvalidArgument
            If event name is not valid.
        DisallowedValuesError
            If an argument value is not in the allowed values.
        """
        if event_name is None or callback is None:
            raise InvalidArgument("'event_name' and 'callback' ")

        if event_name not in self.events_list:
            raise DisallowedValuesError("event-name", event_name, self.events_list)
        with self._lock:
            event_name = event_name.lower()
            callback_id = f"{event_name}-{next(self._service_callback_id)}"
            callbacks_map = self._service_callbacks.get(event_name)
            if callbacks_map:
                callbacks_map.update({callback_id: partial(callback, *args, **kwargs)})
            else:
                self._service_callbacks[event_name] = {
                    callback_id: partial(callback, *args, **kwargs)
                }

    def unregister_callback(self, callback_id: str):
        """Unregister the callback.

        Parameters
        ----------
        callback_id : str
            ID of the registered callback.
        """
        with self._lock:
            for callbacks_map in self._service_callbacks.values():
                if callback_id in callbacks_map:
                    del callbacks_map[callback_id]

    @property
    def events_list(self) -> List[str]:
        """Get a list of supported events.

        Parameters
        ----------
        None

        Returns
        -------
        List[str]
            List of supported events.
        """
        return self._events_list
