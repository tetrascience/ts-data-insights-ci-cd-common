import json
import pathlib
from io import StringIO
from textwrap import dedent

import pytest
from astroid import extract_node, nodes
from deprecation_checker import TaskScriptUtilDeprecationChecker
from pylint.lint import Run, pylinter
from pylint.reporters import JSONReporter
from pylint.reporters.text import TextReporter
from pylint.testutils import CheckerTestCase, MessageTest


class TestImportOldDatetimeParser(CheckerTestCase):
    CHECKER_CLASS = TaskScriptUtilDeprecationChecker

    def setup_method(self):
        """Reset the checker for when running test cases"""
        super().setup_method()
        self.checker._ts_task_script_util_imports = {}

    def test_unroll_function_attribute(self):
        """Test unrolling calls works as intended when the call is an attribute"""
        # Arrange
        node = extract_node("a.b.c.d.e()")

        # Act
        actual = self.checker.unroll_function(node.func)

        # Assert
        assert isinstance(node.func, nodes.Attribute)
        assert actual == ["a", "b", "c", "d", "e"]

    def test_unroll_function_name(self):
        """Test unrolling calls works as intended when the call is a name"""
        # Arrange
        node = extract_node("a()")

        # Act
        actual = self.checker.unroll_function(node.func)

        # Assert
        assert isinstance(node.func, nodes.Name)
        assert actual == ["a"]

    def test_unroll_function_other(self):
        """Test unrolling calls works as intended when the call can't be unrolled to only attributes and names"""
        # Arrange
        node = extract_node("foo[0].bar()")

        # Act
        actual = self.checker.unroll_function(node.func)

        # Assert
        assert actual == []

    @pytest.mark.parametrize(
        "untracked_import",
        [
            "import math",
            "import os, sys",
            "import pathlib.Path as p",
        ],
    )
    def test_untracked_imports(self, untracked_import):
        """Test that normal imports are not tracked"""
        # Arrange
        node = extract_node(untracked_import)

        # Act
        self.checker.visit_import(node)

        # Assert
        assert self.checker._ts_task_script_util_imports == {}

    def test_import_task_script_utils_base(self):
        """Test that importing task_script_utils is tracked"""
        # Arrange
        node = extract_node("import task_script_utils")

        # Act/Assert
        self.checker.visit_import(node)

        # Assert
        assert self.checker._ts_task_script_util_imports == {
            "task_script_utils": "task_script_utils"
        }

    def test_import_task_script_utils_child_module(self):
        """Test that importing a module inside task_script_utils is tracked"""
        # Arrange
        node = extract_node("import task_script_utils.datetime_parser")

        # Act/Assert
        self.checker.visit_import(node)

        # Assert
        assert self.checker._ts_task_script_util_imports == {
            "task_script_utils.datetime_parser": "task_script_utils.datetime_parser"
        }

    def test_import_task_script_utils_child_module_with_alias(self):
        """Test that importing a module inside task_script_utils is tracked via its alias"""
        # Arrange
        node = extract_node("import task_script_utils.datetime_parser as dtp")

        # Act
        self.checker.visit_import(node)

        # Assert
        assert self.checker._ts_task_script_util_imports == {
            "dtp": "task_script_utils.datetime_parser"
        }

    def test_import_from_task_script_utils_base(self):
        """Test that using from task_script_utils import [...] is correctly tracked"""
        # Arrange
        node = extract_node("from task_script_utils import datetime_parser")

        # Act
        self.checker.visit_importfrom(node)

        # Assert
        assert self.checker._ts_task_script_util_imports == {
            "datetime_parser": "task_script_utils.datetime_parser"
        }

    def test_import_from_task_script_utils_child(self):
        """Test that using from task_script_utils.child_module import [...] is correctly tracked"""
        # Arrange
        node = extract_node("from task_script_utils.datetime_parser import parser")

        # Act
        self.checker.visit_importfrom(node)

        # Assert
        assert self.checker._ts_task_script_util_imports == {
            "parser": "task_script_utils.datetime_parser.parser"
        }

    def test_import_from_task_script_utils_alias(self):
        """Test that using from task_script_utils.child_module import [...] as alias is correctly tracked"""
        # Arrange
        node = extract_node(
            "from task_script_utils.datetime_parser import parser as dt_parser"
        )

        # Act
        self.checker.visit_importfrom(node)

        # Assert
        assert self.checker._ts_task_script_util_imports == {
            "dt_parser": "task_script_utils.datetime_parser.parser"
        }

    def test_deprecated_call(self):
        """Test call of deprecated function from imported module"""
        # Arrange
        import_node, call_node = extract_node(
            dedent(
                """
                import task_script_utils.datetime_parser as dtp #@

                dtp.parse('something') #@
                """
            )
        )

        # Act/Assert
        with self.assertNoMessages():
            # import should not be flagged
            self.checker.visit_import(import_node)
        with self.assertAddsMessages(
            MessageTest(
                msg_id="deprecated-task-script-util-datetime-parser-use",
                node=call_node,
                line=4,
                col_offset=0,
            )
        ):
            # call should be flagged
            self.checker.visit_call(call_node)

    def test_deprecated_function_imported(self):
        """Test import of deprecated function directly"""
        # Arrange
        import_node, call_node = extract_node(
            dedent(
                """
                from task_script_utils.datetime_parser import parse #@

                parse('something') #@
                """
            )
        )

        # Act/Assert
        with self.assertAddsMessages(
            MessageTest(
                msg_id="deprecated-task-script-util-datetime-parser-import",
                node=import_node,
                line=2,
                col_offset=0,
            )
        ):
            # import should be flagged
            self.checker.visit_importfrom(import_node)
        with self.assertAddsMessages(
            MessageTest(
                msg_id="deprecated-task-script-util-datetime-parser-use",
                node=call_node,
                line=4,
                col_offset=0,
            )
        ):
            # call should be flagged
            self.checker.visit_call(call_node)

    @pytest.mark.parametrize(
        "valid_import",
        [
            "from pathlib import Path",
            "from unittest.mock import MagicMock as DavidBlaine",
            "from task_script_utils.datetime_parser import DatetimeConfig",
            "from task_script_utils.datetime_parser.parser_exceptions import DatetimeParserError",
            "from task_script_utils.datetime_parser.utils import parsing",
            "from task_script_utils.datetime_parser.utils.parsing import parse_with_formats",
        ],
    )
    def test_import_from_valid_module(self, valid_import):
        """Test that importing any old module does not add any flags"""
        # Arrange
        node = extract_node(valid_import)

        # Act/Assert
        with self.assertNoMessages():
            self.checker.visit_importfrom(node)

    @pytest.mark.parametrize(
        "failing_import",
        [
            "import task_script_utils.datetime_parser.parse",
            "import task_script_utils.datetime_parser.parse as alias",
            "import task_script_utils.datetime_parser.parser",
            "import task_script_utils.datetime_parser.parser as alias",
            "import os, task_script_utils.datetime_parser.parser",
        ],
    )
    def test_import_module_directly(self, failing_import):
        """Test importing the old datetime parser module directly"""
        # Arrange
        node = extract_node(failing_import)

        # Act/Assert
        with self.assertAddsMessages(
            MessageTest(
                msg_id="deprecated-task-script-util-datetime-parser-import",
                node=node,
                line=1,
                col_offset=0,
            )
        ):
            self.checker.visit_import(node)


def test_integration(snapshot) -> None:
    """
    Integration test running this pylint plugin against a real file
    """
    # Arrange
    file_to_lint = pathlib.Path(__file__).parent.joinpath(
        "error_examples",
        "datetime_parser_deprecation.py",
    )
    # Cache for the pylint results.
    json_reporter = JSONReporter()

    # Act
    # Run pylint programmatically.
    Run(
        [
            "--disable",
            "all",
            "--enable",
            "deprecated-task-script-util-datetime-parser-use,deprecated-task-script-util-parser-import",
            "--load-plugins",
            "deprecation_checker",
            "--score",
            "n",
            str(file_to_lint),
        ],
        reporter=json_reporter,
        do_exit=False,
    )

    # Assert
    # Copy from `JSONReporter.display_messages`.
    # "path" key is removed because it depends on the folder from which `pytest`
    # is executed and is therefore fragile.
    pylint_result = [
        {
            "type": message.category,
            "module": message.module,
            "obj": message.obj,
            "line": message.line,
            "column": message.column,
            "endLine": message.end_line,
            "endColumn": message.end_column,
            "symbol": message.symbol,
            "message": message.msg or "",
            "message-id": message.msg_id,
        }
        for message in json_reporter.messages
    ]
    snapshot.assert_match(pylint_result)
