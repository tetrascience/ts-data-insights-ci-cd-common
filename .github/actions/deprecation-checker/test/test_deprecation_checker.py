import json
import pathlib
from io import StringIO
from textwrap import dedent

from astroid import extract_node
from deprecation_checker import ContextAPIDeprecationChecker
from pylint.lint import Run, pylinter
from pylint.reporters import JSONReporter
from pylint.reporters.text import TextReporter
from pylint.testutils import CheckerTestCase, MessageTest


class TestUniqueReturnChecker(CheckerTestCase):
    CHECKER_CLASS = ContextAPIDeprecationChecker

    def test_one_arg(self):
        # fmt: off
        node = extract_node(
            dedent(
                """
                from ts_sdk.task import Context

                context = Context()
                context.write_file(file_category='IDS')
                """
            )
        )
        # fmt: on
        with self.assertAddsMessages(
            MessageTest(
                msg_id="deprecated-context-api",
                node=node,
                line=5,
                col_offset=0,
            )
        ):
            self.checker.visit_call(node)

    def test_multiple_args(self):
        # fmt: off
        node = extract_node(
            dedent(
                """
                import io
                from ts_sdk.task import Context

                context = Context()
                my_file = io.BytesIO(b"foo")
                context.write_file(my_file, file_category='IDS')
                """
            )
        )
        # fmt: on
        with self.assertAddsMessages(
            MessageTest(
                msg_id="deprecated-context-api",
                node=node,
                line=7,
                col_offset=0,
            )
        ):
            self.checker.visit_call(node)

    def test_no_pylint_errors(self):
        # fmt: off
        node = extract_node(
            dedent(
                """
                my_file = io.BytesIO(b"foo")
                context.write_file(my_file, file_category='FOO')
                """
            )
        )
        # fmt: on
        with self.assertNoMessages():
            self.checker.visit_call(node)


def test_integration(snapshot) -> None:
    """
    Integration test running this pylint plugin against raises_error_example.py.
    """
    # Arrange
    file_to_lint = pathlib.Path(__file__).parent.joinpath(
        "error_examples",
        "context_deprecation.py",
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
            "deprecated-context-api",
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
