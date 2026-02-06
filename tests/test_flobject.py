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

"""Unit tests for flobject module."""

from collections.abc import MutableMapping
from typing import ForwardRef, List, NewType, Union
import weakref

import pytest

from ansys.cfx.core.common import flobject
from ansys.cfx.core.common.flobject import DeprecatedSettingWarning, InactiveObjectError
from ansys.cfx.core.session_pre import PreProcessing


class Setting:
    """Base class for setting objects."""

    def __init__(self, parent):
        self.parent = None if parent is None else weakref.proxy(parent)

    def get_attr(self, attr):
        attrs = self.get_attrs([attr])
        if attrs.get("active?"):
            return attrs[attr]
        else:
            raise RuntimeError("Object is not active")

    def get_attrs(self, attrs):
        active = self.attrs.get("active?", lambda self: True)(self)
        if active:
            return {attr: self.attrs[attr](self) for attr in attrs}
        else:
            return {"active?": False}

    attrs = {
        "active?": lambda self: True,
        "webui-release-active?": lambda self: True,
    }


class PrimitiveSetting(Setting):
    """Primitive setting objects."""

    value = None

    def get_state(self):
        return self.value

    def set_state(self, value):
        self.value = value

    @classmethod
    def get_static_info(cls):
        ret = {"type": cls.objtype}
        if cls.__doc__:
            ret["help"] = cls.__doc__
        return ret


class Bool(PrimitiveSetting):
    objtype = "boolean"


class Int(PrimitiveSetting):
    objtype = "integer"


class Real(PrimitiveSetting):
    objtype = "real"


class String(PrimitiveSetting):
    objtype = "string/symbol"


class BoolList(PrimitiveSetting):
    objtype = "boolean-list"


class IntList(PrimitiveSetting):
    objtype = "integer-list"


class RealList(PrimitiveSetting):
    objtype = "real-list"


class StringList(PrimitiveSetting):
    objtype = "string-list"


class Group(Setting):
    """Group objects."""

    objtype = "group"
    children = {}
    commands = {}

    def __init__(self, parent):
        super().__init__(parent)
        self.objs = {c: v(self) for c, v in self.children.items()}

    def get_state(self):
        ret = {}
        for c in self.children:
            cobj = self.objs[c]
            if cobj.get_attr("active?"):
                ret[c] = cobj.get_state()
        return ret

    def set_state(self, value):
        for c in self.children:
            v = value.get(c)
            if v is not None:
                self.objs[c].set_state(v)

    def get_child(self, c):
        return self.objs[c]

    def get_command(self, c):
        return self.commands[c](self)

    @classmethod
    def get_static_info(cls):
        ret = {"type": cls.objtype}
        if cls.__doc__:
            ret["help"] = cls.__doc__
        if cls.children:
            ret["children"] = {c: v.get_static_info() for c, v in cls.children.items()}
        if cls.commands:
            ret["commands"] = {c: v.get_static_info() for c, v in cls.commands.items()}
        if cls.child_aliases:
            ret["child_aliases"] = cls.child_aliases
        return ret


class NamedObject(Setting, MutableMapping):
    """NamedObject class."""

    objtype = "named-object"
    commands = {}
    # To be overridden by child classes
    # child_object_type = None

    def __init__(self, parent):
        super().__init__(parent)
        self._objs = {}

    def __getitem__(self, name):
        return self._objs[name].get_state()

    def __setitem__(self, name, value):
        if name not in self._objs:
            self._objs[name] = self.child_object_type(self)
        return self._objs[name].set_state(value)

    def __delitem__(self, name):
        del self._objs[name]

    def __iter__(self):
        return iter(self._objs)

    def __len__(self):
        return len(self._objs)

    def get_child(self, c):
        return self._objs[c]

    def rename(self, new, old):
        self._objs = {(new if k == old else k): v for k, v in self._objs.items()}

    def get_object_names(self):
        return list(self._objs.keys())

    def get_command(self, c):
        return self.commands[c](self)

    def get_state(self):
        return {c: v.get_state() for c, v in self._objs.items()}

    def set_state(self, state):
        for k, v in state.items():
            self[k] = v

    @classmethod
    def get_static_info(cls):
        ret = {"type": cls.objtype}
        if cls.__doc__:
            ret["help"] = cls.__doc__
        ret["object-type"] = cls.child_object_type.get_static_info()
        if cls.commands:
            ret["commands"] = {c: v.get_static_info() for c, v in cls.commands.items()}
        try:
            if cls.user_creatable:
                ret["user_creatable"] = cls.user_creatable
        except AttributeError:
            ret["user_creatable"] = True
        if cls.child_aliases:
            ret["child_aliases"] = cls.child_aliases
        return ret


class ListObject(Setting):
    """ListObject class."""

    objtype = "list-object"
    commands = {}
    # To be overridden by child classes
    # child_object_type = None

    def __init__(self, parent):
        super().__init__(parent)
        self._objs = []

    def __getitem__(self, index):
        return self._objs[index].get_state()

    def __setitem__(self, index, value):
        return self._objs[index].set_state(value)

    def __iter__(self):
        return iter(self._objs)

    def __len__(self):
        return len(self._objs)

    def size(self):
        return len(self._objs)

    def resize(self, l):
        if l > len(self._objs):
            # pylint: disable=unused-variable
            for i in range(len(self._objs), l):
                self._objs.append(self.child_object_type(self))
        elif l < len(self._objs):
            self._objs = self._objs[:l]

    def get_child(self, c):
        return self._objs[int(c)]

    def get_command(self, c):
        return self.commands[c](self)

    def get_state(self):
        return [x.get_state() for x in self._objs]

    def set_state(self, value):
        self.resize(len(value))
        for i, v in enumerate(value):
            self[i] = v

    @classmethod
    def get_static_info(cls):
        ret = {"type": cls.objtype}
        if cls.__doc__:
            ret["help"] = cls.__doc__
        ret["object-type"] = cls.child_object_type.get_static_info()
        if cls.commands:
            ret["commands"] = {c: v.get_static_info() for c, v in cls.commands.items()}
        if cls.queries:
            ret["queries"] = {c: v.get_static_info() for c, v in cls.queries.items()}
        if cls.child_aliases:
            ret["child_aliases"] = cls.child_aliases
        return ret


class Command(Setting):
    """Command class."""

    objtype = "command"
    # To be overridden by child classes
    # arguments = None
    # cb = None

    def __call__(self, **kwds):
        args = []
        for k, v in self.arguments.items():
            a = kwds.get(k, v(self).get_state())
            args.append(a)
        return self.cb(*args)

    @classmethod
    def get_static_info(cls):
        ret = {"type": cls.objtype}
        if cls.__doc__:
            ret["help"] = cls.__doc__
        if cls.arguments:
            ret["arguments"] = {c: v.get_static_info() for c, v in cls.arguments.items()}
        if cls.child_aliases:
            ret["child_aliases"] = cls.child_aliases
        return ret


class Query(Setting):
    """Query class."""

    objtype = "query"
    # To be overridden by child classes
    # arguments = None
    # cb = None

    def __call__(self, **kwds):
        args = []
        for k, v in self.arguments.items():
            a = kwds.get(k, v(self).get_state())
            args.append(a)
        return self.cb(*args)

    @classmethod
    def get_static_info(cls):
        ret = {"type": cls.objtype}
        if cls.__doc__:
            ret["help"] = cls.__doc__
        if cls.arguments:
            ret["arguments"] = {c: v.get_static_info() for c, v in cls.arguments.items()}
        return ret


class Root(Group):
    """Root class."""

    class G1(Group):
        class S1(String):
            attrs = {
                "active?": lambda self: not self.parent.objs["b-3"].get_state(),
                "allowed-values": lambda self: ["foo", "bar"],
                "webui-release-active?": lambda self: True,
            }

        children = {
            "r-1": Real,
            "i-2": Int,
            "b-3": Bool,
            "s-4": S1,
        }

        child_aliases = {"i-2_old": "i-2", "gc-1_old": "../c-1", "gn-1_old": "../n-1"}

    class N1(NamedObject):
        class NC(Group):
            children = {
                "rl-1": RealList,
                "sl-1": StringList,
            }
            child_aliases = {}

        child_object_type = NC

        child_aliases = {"nc-1_old": "../c-1"}

    class L1(ListObject):
        # List testing in this file is expanded as it is not currently testable any other way
        class LC(Group):
            children = {
                "il-1": IntList,
                "bl-1": BoolList,
            }
            child_aliases = {}

        child_object_type = LC

        child_aliases = {"lc-1_old": "../c-1"}

        class ListCommand(Command):
            """ListCommand class."""

            class A1(Real):
                value = 2.3

            class A2(Bool):
                value = True

            arguments = {
                "a-1": A1,
                "a-2": A2,
            }

            child_aliases = {}

            def cb(self, a1, a2):
                if a2 is True:
                    self.parent.objs["g-1"].objs["r-1"].value += a1
                else:
                    self.parent.objs["g-1"].objs["r-1"].value -= a1

        class ListQuery(Query):
            """ListQuery class."""

            class A1(Real):
                value = 2.3

            class A2(Bool):
                value = True

            arguments = {
                "a-1": A1,
                "a-2": A2,
            }

            def cb(self, a1, a2):
                if a2 is True:
                    self.parent.objs["g-1"].objs["r-1"].value += a1
                else:
                    self.parent.objs["g-1"].objs["r-1"].value -= a1

        commands = {
            "c-1": ListCommand,
        }
        queries = {
            "q-1": ListQuery,
        }

    class Command1(Command):
        """Command1 class."""

        class A1(Real):
            value = 2.3

        class A2(Bool):
            value = True

        arguments = {
            "a-1": A1,
            "a-2": A2,
        }

        child_aliases = {"a-1_old": "a-1"}

        def cb(self, a1, a2):
            if a2 is True:
                self.parent.objs["g-1"].objs["r-1"].value += a1
            else:
                self.parent.objs["g-1"].objs["r-1"].value -= a1

    class Command2(Command):
        """Command2 class, returns a value."""

        arguments = {"a-1": Real}

        child_aliases = {}

        def cb(self, a1):
            return a1

    children = {
        "g-1": G1,
        "n-1": N1,
        "l-1": L1,
    }

    commands = {
        "c-1": Command1,
        "c-2": Command2,
    }

    child_aliases = {"n-1_old": "n-1", "l-1_old": "l-1", "c-1_old": "c-1", "gs-4_old": "g-1/s-4"}


class Proxy:
    """Proxy class."""

    root = Root

    def __init__(self):
        self.r = self.root(None)

    def get_obj(self, path):
        if not path:
            return self.r
        obj = self.r
        for c in path.split("/"):
            try:
                obj = obj.get_child(c)
            except KeyError:
                obj = obj.get_command(c)
        return obj

    def get_var(self, path):
        return self.get_obj(path).get_state()

    def set_var(self, path, value):
        try:
            return self.get_obj(path).set_state(value)
        except KeyError:
            # Try creating the object first.
            # The PyCFX engines do not need the object to exist before setting its state
            parent_path, name = path.rsplit("/", 1)
            self.create(parent_path, name)
            return self.get_obj(path).set_state(value)

    def rename(self, path, new, old):
        return self.get_obj(path).rename(new, old)

    def create(self, path, name):
        self.get_obj(path)[name] = {}

    def delete(self, path, name):
        del self.get_obj(path)[name]

    def resize_list_object(self, path, size):
        return self.get_obj(path).resize(size)

    def get_list_size(self, path):
        return self.get_obj(path).size()

    def get_object_names(self, path):
        return self.get_obj(path).get_object_names()

    def execute_cmd(self, path, command, **kwds):
        return self.get_obj(path).get_command(command)(**kwds)

    def get_attrs(self, path, attrs, recursive=False):
        return self.get_obj(path).get_attrs(attrs)

    def has_wildcard(self, name):
        return False

    @classmethod
    def get_static_info(cls):
        return cls.root.get_static_info()

    def is_interactive_mode(self):
        return False


class InfoQuery:
    """InfoQuery class."""

    def __init__(self):
        pass


def test_primitives():
    r = flobject.get_root(Proxy())
    r.g_1.r_1 = 3.2
    assert r.g_1.r_1() == 3.2
    r.g_1.i_2 = -3
    assert r.g_1.i_2() == -3
    r.g_1.b_3 = True
    assert r.g_1.b_3() is True
    r.g_1.b_3 = False
    assert r.g_1.b_3() is False
    r.g_1.s_4 = "foo"
    assert r.g_1.s_4() == "foo"


def test_group():
    r = flobject.get_root(Proxy())
    r.g_1 = {"r_1": 3.2, "i_2": -3, "b_3": False, "s_4": "foo"}
    assert r.g_1() == {"r_1": 3.2, "i_2": -3, "b_3": False, "s_4": "foo"}
    r.g_1 = {"s_4": "bar"}
    assert r.g_1() == {"r_1": 3.2, "i_2": -3, "b_3": False, "s_4": "bar"}
    r.g_1.i_2 = 4
    assert r.g_1() == {"r_1": 3.2, "i_2": 4, "b_3": False, "s_4": "bar"}


def test_settings_input_set_state():
    r = flobject.get_root(Proxy())
    r.g_1 = {"r_1": 3.2, "i_2": -3, "b_3": False, "s_4": "foo"}
    r.g_1.set_state(r_1=3.2, i_2=-3, b_3=False, s_4="foo")
    assert r.g_1() == {"r_1": 3.2, "i_2": -3, "b_3": False, "s_4": "foo"}
    r.g_1.set_state(s_4="bar")
    assert r.g_1() == {"r_1": 3.2, "i_2": -3, "b_3": False, "s_4": "bar"}
    r.g_1.set_state(i_2=4)
    assert r.g_1() == {"r_1": 3.2, "i_2": 4, "b_3": False, "s_4": "bar"}


def test_settings_input():
    r = flobject.get_root(Proxy())
    r.g_1 = {"r_1": 3.2, "i_2": -3, "b_3": False, "s_4": "foo"}
    r.g_1(r_1=3.2, i_2=-3, b_3=False, s_4="foo")
    assert r.g_1() == {"r_1": 3.2, "i_2": -3, "b_3": False, "s_4": "foo"}
    r.g_1(s_4="bar")
    assert r.g_1() == {"r_1": 3.2, "i_2": -3, "b_3": False, "s_4": "bar"}
    r.g_1(i_2=4)
    assert r.g_1() == {"r_1": 3.2, "i_2": 4, "b_3": False, "s_4": "bar"}


def test_named_object():
    r = flobject.get_root(Proxy())
    assert r.n_1.get_object_names() == []
    r.n_1["n1"] = {}
    r.n_1["n2"] = {}
    assert r.n_1.get_object_names() == ["n1", "n2"]
    r.n_1.create("n4")
    assert r.n_1.get_object_names() == ["n1", "n2", "n4"]
    del r.n_1["n1"]
    assert r.n_1.get_object_names() == ["n2", "n4"]
    r.n_1["n1"] = {"rl_1": [1.2, 3.4], "sl_1": ["foo", "bar"]}
    assert r.n_1["n1"]() == {"rl_1": [1.2, 3.4], "sl_1": ["foo", "bar"]}
    r.n_1 = {"n5": {"rl_1": [4.3, 2.1], "sl_1": ["oof", "rab"]}}
    assert r.n_1.get_object_names() == ["n2", "n4", "n1", "n5"]
    assert r.n_1["n5"]() == {"rl_1": [4.3, 2.1], "sl_1": ["oof", "rab"]}


def test_list_object():
    r = flobject.get_root(Proxy())
    assert r.l_1.get_size() == 0
    r.l_1 = [
        {"il_1": None, "bl_1": None},
        {"il_1": None, "bl_1": None},
    ]
    r.l_1[1].il_1 = [1, 2]
    assert r.l_1() == [
        {"il_1": None, "bl_1": None},
        {"il_1": [1, 2], "bl_1": None},
    ]
    r.l_1 = [{"il_1": [3], "bl_1": [True, False]}]
    assert r.l_1() == [{"il_1": [3], "bl_1": [True, False]}]

    # List testing in this file is expanded as it is not currently testable any other way
    assert r.l_1.to_engine_keys({"Simple Value"}) == {"Simple Value"}
    assert r.l_1.to_python_keys({"Simple Value"}) == {"Simple Value"}
    assert len(r.l_1) == 1

    r.l_1 = [
        {"il_1": [3], "bl_1": [True, False]},
        {"il_1": [1, 2], "bl_1": None},
    ]
    r.l_1[1] = {"il_1": [5, 3], "bl_1": None}
    assert r.l_1() == [
        {"il_1": [3], "bl_1": [True, False]},
        {"il_1": [5, 3], "bl_1": None},
    ]

    try:
        val = r.l_1.bad_attr
    except AttributeError as e:
        assert str(e) == "'super' object has no attribute 'bad_attr'"
    else:
        assert False, "Expected AttributeError"

    list_iter = iter(r.l_1)
    next(list_iter)
    next(list_iter)
    try:
        next(list_iter)
    except StopIteration:
        pass
    else:
        assert False, "Expected StopIteration"

    try:
        obj = r.l_1[10]
    except IndexError as e:
        assert str(e) == "10"
    else:
        assert False, "Expected IndexError"


def test_command():
    r = flobject.get_root(Proxy())
    r.g_1.r_1 = 2.4
    r.c_1()
    assert r.g_1.r_1() == 2.4 + 2.3
    r.c_1(a_2=False)
    assert r.g_1.r_1() == 2.4 + 2.3 - 2.3
    r.c_1(a_1=3.2, a_2=True)
    assert r.g_1.r_1() == 2.4 + 2.3 - 2.3 + 3.2
    r.c_1(a_1=4.5, a_2=False)
    assert r.g_1.r_1() == 2.4 + 2.3 - 2.3 + 3.2 - 4.5

    r.c_2._setattr("return_type", "integer")
    assert r.c_2(a_1=5) == 5
    try:
        r.c_2(a_1="AA")
    except TypeError as e:
        assert str(e) == "AA is not of type <class 'int'>."
    else:
        assert False, "Expected TypeError"


def test_attrs():
    r = flobject.get_root(Proxy())
    assert r.g_1.s_4.get_attr("active?")
    assert r.g_1.s_4.get_attr("allowed-values") == ["foo", "bar"]
    r.g_1.b_3 = True
    assert not r.g_1.s_4.get_attr("active?")
    with pytest.raises(InactiveObjectError) as einfo:
        r.g_1.s_4.get_attr("allowed-values") == ["foo", "bar"]


def test_aliases():
    r = flobject.get_root(Proxy(), "", None, None, InfoQuery())

    # The mock class creation doesn't currently set up child aliases correctly if the alias is a
    # path, so just fix it here.
    r.g_1._child_aliases["gc_1_old"] = "../c_1"
    r.g_1._child_aliases["gn_1_old"] = "../n_1"
    r.n_1._child_aliases["nc_1_old"] = "../c_1"
    r.l_1._child_aliases["lc_1_old"] = "../c_1"

    r.g_1 = {"r_1": 3.2, "i_2": 4, "b_3": False, "s_4": "bar"}

    with pytest.warns(DeprecatedSettingWarning) as warning_log:
        r.g_1.i_2_old = 77
    assert r.g_1() == {"r_1": 3.2, "i_2": 77, "b_3": False, "s_4": "bar"}
    assert len(warning_log) == 2
    assert warning_log[0].message.args[0] == (
        "Note: A newer syntax is available to perform the last operation.\n"
    )
    assert warning_log[1].message.args[0] == (
        "\n"
        "Execute the following code to suppress future warnings like the above:\n"
        "\n"
        ">>> import warnings\n"
        '>>> warnings.filterwarnings("ignore", category=DeprecatedSettingWarning)'
    )

    r.n_1["n1"] = {}
    r.n_1_old["n2"] = {}
    assert r.n_1.get_object_names() == ["n1", "n2"]
    r.n_1_old.rename("n1_new", "n1")
    assert r.n_1.get_object_names() == ["n1_new", "n2"]
    del r.n_1_old["n2"]
    assert r.n_1_old.get_object_names() == ["n1_new"]
    r.n_1_old.nc_1_old()
    assert r.g_1.r_1() == 3.2 + 2.3

    r.l_1 = [
        {"il_1": None, "bl_1": None},
        {"il_1": None, "bl_1": None},
    ]
    assert r.l_1_old.get_size() == 2
    r.l_1.lc_1_old()
    assert r.g_1.r_1() == 3.2 + 2.3 + 2.3

    r.g_1.r_1 = 2.4
    r.c_1_old()
    assert r.g_1.r_1() == 2.4 + 2.3

    r.g_1.gc_1_old()
    assert r.g_1.r_1() == 2.4 + 2.3 + 2.3

    r.set_state(
        {
            "g_1": {"r_1": 3.2, "i_2": 33, "b_3": False, "s_4": "bar"},
            "n_1_old": {"n1_new": {"rl_1": None, "sl_1": ["aa", "bb"]}},
            "l_1": [{"il_1": None, "bl_1": None}, {"il_1": None, "bl_1": None}],
        }
    )
    assert r.g_1.i_2() == 33
    assert r.n_1["n1_new"].sl_1() == ["aa", "bb"]

    r.g_1.r_1 = 2.4
    r.c_1(a_1=5.0)
    assert r.g_1.r_1() == 2.4 + 5.0
    r.c_1(a_1_old=4.0)
    assert r.g_1.r_1() == 2.4 + 5.0 + 4.0

    # Alias to parent
    try:
        r.g_1.set_state(
            {
                "r_1": 3.2,
                "i_2": 33,
                "b_3": False,
                "s_4": "bar",
                "gn_1_old": {"n1_new": {"rl_1": None, "sl_1": ["aa", "bb"]}},
            }
        )
    except NotImplementedError as e:
        assert str(e) == ('Cannot handle ".." in alias path while setting dictionary state.')
    else:
        assert False, "Expected NotImplementedError"

    # Alias to child
    r.set_state(
        {
            "gs_4_old": 66,
            "n_1": {"n1_new": {"rl_1": None, "sl_1": ["aa", "bb"]}},
            "l_1": [{"il_1": None, "bl_1": None}, {"il_1": None, "bl_1": None}],
        }
    )
    assert r.g_1.s_4() == 66


def test_to_python_name():
    assert flobject.to_python_name("Simple Value") == "simple_value"
    assert flobject.to_python_name("MASS AND MOMENTUM") == "mass_and_momentum"
    assert flobject.to_python_name("def") == "def_"


def test_accessor_methods_on_settings_object(pre_load_static_mixer_case: PreProcessing):
    pypre = pre_load_static_mixer_case

    boundary_type = (
        pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"].boundary_type
    )

    existing = boundary_type.get_attr("allowed-values")
    modified = boundary_type.allowed_values()
    assert existing == modified

    existing = boundary_type.get_attr("read-only?", bool)
    modified = boundary_type.is_read_only()
    assert existing == modified


def test_find_children(pre_load_static_mixer_case: PreProcessing):

    pypre = pre_load_static_mixer_case

    boundary_contour = (
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary["in1"]
        .boundary_contour
    )

    assert (len(flobject.find_children(pypre.setup))) > 8000

    assert flobject.find_children(boundary_contour) == [
        "enabled",
        "profile_variable",
        "profile_reference_object",
        "visibility",
    ]

    assert flobject.find_children(boundary_contour, identifier="pr*") == [
        "profile_variable",
        "profile_reference_object",
    ]

    assert flobject.find_children(
        pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"],
        identifier="prof*",
    ) == [
        "boundary_profile/profile_name",
        "boundary_contour/profile_variable",
        "boundary_contour/profile_reference_object",
        "boundary_vector/profile_vector_components",
    ]


def test_check_type(pre_load_static_mixer_case: PreProcessing):

    pypre = pre_load_static_mixer_case
    boundary = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"]
    pressure = boundary.boundary_conditions.mass_and_momentum.relative_pressure
    water_group = pypre.setup.library.material["Water"].material_group()

    DerivedStr = NewType("DerivedStr", str)

    input = [
        (boundary.boundary_contour, int, False),
        (boundary.boundary_contour, flobject.Group, True),
        (boundary.boundary_contour, flobject.NamedObject, False),
        (boundary, flobject.NamedObject, False),
        (pressure, flobject.RealNumerical, True),
        (boundary, Union[flobject.Group, flobject.NamedObject], True),
        (boundary, dict[int, int], False),
        (water_group, list[int], False),
        (water_group, list[str], True),
        (water_group, set[str], False),
        (water_group, List[ForwardRef("str")], True),
        (boundary, tuple[int, float], False),
        (boundary.boundary_type, DerivedStr, False),
        (boundary, "BadType", False),
    ]

    for item, pos_type, result in input:
        assert flobject.check_type(item, pos_type) == result


def test_miscellaneous_functions(pre_load_static_mixer_case: PreProcessing, capsys):

    pypre = pre_load_static_mixer_case
    boundary = pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"]
    boundary_contour = boundary.boundary_contour

    assert (
        boundary_contour.parent.path
        == "setup/FLOW/Flow Analysis 1/DOMAIN/Default Domain/BOUNDARY/in1"
    )

    try:
        bad_bc = (
            pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["Bad Boundary"]
        )
    except KeyError as e:
        assert str(e) == (
            "\"'boundary' has no attribute 'Bad Boundary'.\\n"
            "The allowed values are: ['Default Domain Default', 'in1', 'in2', 'out'].\""
        )
    else:
        assert False, "Expected KeyError"

    try:
        pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary[
            "in1"
        ].boundary_conditions.option = "Invalid Option"
    except AttributeError as e:
        msg = (
            "'boundary_conditions' object has no attribute 'option'.\n"
            "The most similar names are: mesh_motion..\nThe most similar names are: mesh_motion."
        )
        assert str(e) == msg
    else:
        assert False, "Expected AttributeError"
    captured = capsys.readouterr()
    assert (
        captured.out == "\n"
        " option can be accessed from the following paths: \n\n"
        '    <session>.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"].'
        "boundary_conditions.flow_regime.option\n"
        '    <session>.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"].'
        "boundary_conditions.mass_and_momentum.option\n"
        '    <session>.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"].'
        "boundary_conditions.turbulence.option\n"
        '    <session>.setup.flow["Flow Analysis 1"].domain["Default Domain"].boundary["in1"].'
        "boundary_conditions.heat_transfer.option\n"
    )

    assert (
        pypre.setup.flow["Flow Analysis 1"]
        .domain["Default Domain"]
        .boundary["in1"]
        .find_object("../../fluid_models")
    )

    # Internal function test (can't be accessed with valid engine values)
    try:
        pypre.setup.flow["Flow Analysis 1"].domain["Default Domain"]._add_units_to_state(
            {"boundary": {"Bad Boundary": {"option": "Bad"}}}
        )
    except RuntimeError as e:
        assert (
            str(e)
            == "Unexpected None child Bad Boundary encountered while getting units for state."
        )
    else:
        assert False, "Expected RuntimeError"
