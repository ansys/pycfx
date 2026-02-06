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

from ansys.cfx.core.session_post import PostProcessing
from ansys.cfx.core.session_pre import PreProcessing
from ansys.cfx.core.utils.cfx_version import CFXVersion


def test_get_engine_version(pypre: PreProcessing, pytestconfig):

    result = pypre.engine_eval.get_engine_version()
    assert result.startswith("2")


def test_eval_expression(pypre: PreProcessing, pytestconfig):

    try:
        result = pypre.engine_eval.eval_expression("1 [m] + 2 [m]")
    except RuntimeError as e:
        result = str(e)
    if pypre.get_cfx_version() < CFXVersion.v261:
        msg = (
            "eval_expression is not supported before Release 26.1. "
            "Expressions can be created and evaluated from the 'expressions' object."
        )
        assert result == msg
    else:
        assert result == "3 [m]"


def test_eval_expression_error(pypost: PostProcessing, pytestconfig):

    try:
        result = pypost.engine_eval.eval_expression("1 [K] + MyUndefinedTemp")
    except Exception as e:
        result = str(e)
    if pypost.get_cfx_version() > CFXVersion.v252:
        # This should be changed to test for equality once the error is caught properly
        assert "The following unrecognised name was referenced: MyUndefinedTemp." in result


def test_process_ccl(pypre: PreProcessing, pytestconfig):
    ccl_str = """
        LIBRARY:
          CEL:
            EXPRESSIONS:
              Expr1 = 5 [K]
            END
          END
        END
    """
    pypre.engine_eval.process_ccl([ccl_str])

    result = pypre.engine_eval.info_query("Engine State")
    assert "Expr1 = 5 [K]" in result


# Test can't be run until error handling is fixed
# def test_process_ccl_error(pypre: PreProcessing, pytestconfig):
#    if pypost.get_cfx_version() > CFXVersion.v252:
#      ok = False
#      try:
#          ccl_str = """
#              LIBRARY:
#                CEL:
#                  Bad Parameter = 44
#                END
#              END
#          """
#          pypre.engine_eval.process_ccl([ccl_str])
#
#      except Exception as e:
#          assert str(e) == " error not known yet "
#          ok = True
#
#      assert ok


def test_info_query(pypost: PostProcessing, pytestconfig):

    result = pypost.engine_eval.info_query("Engine Rules")
    assert "RULES:" in result


def test_info_query_error(pypost: PostProcessing, pytestconfig):

    if pypost.get_cfx_version() > CFXVersion.v252:
        result = pypost.engine_eval.info_query("bad query")
        assert result == "ERROR: No query 'bad query'."
