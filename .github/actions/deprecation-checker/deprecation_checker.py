"""Check for deprecated usages of the :meth:`ts_sdk.task.Context.write_file` method.

.. code-block:: console

    $ pylint \
        --disable=all \
        --enable=deprecated-context-api \
        --load-plugins=deprecation_checker \
        --score=n \
        test/raises_error_example.py

    ************* Module test.raises_error_example
    test/raises_error_example.py:1:0: W1504: Deprecated argument 'IDS' passed to Context.write_file() (deprecated-context-api)
    test/raises_error_example.py:6:4: W1504: Deprecated argument 'IDS' passed to Context.write_file() (deprecated-context-api)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from astroid import nodes
from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter


class ContextAPIDeprecationChecker(BaseChecker):
    """
    Implement the pylint plugin that checks for deprecated usage of
    :class:`ts_sdk.task.__task_script_runner.Context.write_file`.
    """

    # Note: the pylint plugin breaks without setting ``__implements__``.
    __implements__ = (IAstroidChecker,)

    name = "context-api"
    #: Messages to register with pylint and potentially display.
    msgs = {
        "W1504": (
            "Deprecated argument 'IDS' passed to Context.write_file()",
            "deprecated-context-api",
            "file_category='IDS' is deprecated and will be removed in the future.",
        ),
    }

    def visit_call(self, node: nodes.Call) -> None:
        """Visit an AST node calling a function."""
        # ``if`` statements copied from
        # :meth:``pylint.checkers.deprecated.DeprecatedMixin.check_deprecated_method``
        if isinstance(node.func, nodes.Attribute):
            function_name = node.func.attrname
        elif isinstance(node.func, nodes.Name):
            function_name = node.func.name
        else:
            # Not interested in other nodes.
            return

        if function_name != "write_file":
            return
        for arg in node.keywords:
            argname = arg.arg
            if argname != "file_category":
                continue
            if hasattr(arg.value, "value") and arg.value.value == "IDS":
                # If `write_file` is passed a variable, `arg.value` will not have
                # attribute `value`. In this case, it's not possible to infer whether
                # it's value is "IDS".
                self.add_message("deprecated-context-api", node=node)
            return


def register(linter: PyLinter) -> None:
    """Enable loading this plugin."""
    linter.register_checker(ContextAPIDeprecationChecker(linter))
