"""Check for deprecated usages, such as of the :meth:`ts_sdk.task.Context.write_file` method.

.. code-block:: console

    $ pylint \
        --disable=all \
        --enable=deprecated-context-api \
        --load-plugins=deprecation_checker \
        --score=n \
        test/error_examples/context_deprecation.py


    ************* Module context_deprecation
    test/error_examples/context_deprecation.py:1:0: W1599: Deprecated keyword argument file_category='IDS' passed to Context.write_file() (deprecated-context-api)
    test/error_examples/context_deprecation.py:6:4: W1599: Deprecated keyword argument file_category='IDS' passed to Context.write_file() (deprecated-context-api)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List

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
        "W1599": (
            "Deprecated keyword argument file_category='IDS' passed to Context.write_file()",
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


class TaskScriptUtilDeprecationChecker(BaseChecker):
    """
    This checker looks for deprecated usage of code imported from `task_script_utils`.
    """

    # Note: the pylint plugin breaks without setting ``__implements__``.
    __implements__ = (IAstroidChecker,)

    name = "ts-task-script-util"
    #: Messages to register with pylint and potentially display.
    msgs = {
        "W1598": (
            "Use of deprecated datetime parser",
            "deprecated-task-script-util-datetime-parser-use",
            "task_script_utils.parser.parse is deprecated and will be removed in the future. "
            "Use task_script_utils.datetime_parser.utils.parsing.parse_with_formats() instead",
        ),
        "W1597": (
            "Import of deprecated datetime parser",
            "deprecated-task-script-util-datetime-parser-import",
            "task_script_utils.parser.parse is deprecated and will be removed in the future. "
            "Use task_script_utils.datetime_parser.utils.parsing.parse_with_formats() instead",
        ),
    }
    _ts_task_script_util_imports: Dict[str, str] = {}

    def unroll_function(self, func: nodes.NodeNG) -> List[str]:
        """
        Convert a function call into a list of its objects.

        For example, the function call `baz.bar.foo()` will be represented this way by astroid:
        ```
        Attribute(
            attrname="foo",
            expr=Attribute(
                attrname="bar"
                expr=Name("baz")
            )
        )
        ```
        """
        # figure out the module that this call came from
        cur_node = func
        path = []
        while cur_node:
            if isinstance(cur_node, nodes.Attribute):
                # attributes potentially have an expr
                # for example: `a.b()`:
                # Call.func == Attribute(b)
                # Attribute(b).expr == Name(a)
                path.append(cur_node.attrname)
                cur_node = cur_node.expr if hasattr(cur_node, "expr") else None
            elif isinstance(cur_node, nodes.Name):
                path.append(cur_node.name)
                cur_node = None
            else:
                # unknown node, so this could be any number of unexpected scenarios (such as `foo[0].bar()`)
                # it's better to abort than have a confusing message
                return []
        # path is built from the top down but we want it in order, so reverse it
        # example: a.b.c() should return ['a', 'b', 'c']
        path.reverse()
        return path

    def visit_call(self, node: nodes.Call) -> None:
        """Process function call nodes"""

        if not isinstance(node.func, (nodes.Attribute, nodes.Name)):
            # There are calls which either do not have a name or don't have attributes
            # name call looks like `foo()`
            # attribute call looks like `bar.foo()`
            return

        # turn `baz.bar.foo()` into `['baz', 'bar', 'foo']`
        path = self.unroll_function(node.func)

        if not path:
            # no path, no problem.
            return

        # first element of the path is possibly one of our tracked imports
        if path[0] in self._ts_task_script_util_imports:
            path[0] = self._ts_task_script_util_imports[path[0]]

        full_path = ".".join(path)

        if full_path in (
            "task_script_utils.convert_datetime_to_ts_format.convert_datetime_to_ts_format",
        ):
            # the call path for this function is a deprecated function
            self.add_message(
                "deprecated-task-script-util-datetime-parser-use", node=node
            )

    def visit_import(self, node: nodes.Import) -> None:
        """Process nodes that look like `import X`."""
        for module, alias in node.names:
            if "task_script_utils" not in module:
                continue
            if module in (
                "task_script_utils.convert_datetime_to_ts_format",
            ):
                # Direct import of deprecated function or module
                self.add_message(
                    "deprecated-task-script-util-datetime-parser-import", node=node
                )

            # keep track of relevant aliases to check individual calls later
            if alias:
                self._ts_task_script_util_imports[alias] = module
            else:
                self._ts_task_script_util_imports[module] = module

    def visit_importfrom(self, node: nodes.ImportFrom) -> None:
        """Process nodes that look like `from X import Y`."""

        if "task_script_utils" not in node.modname:
            return

        for name, alias in node.names:
            if name  == "convert_datetime_to_ts_format":
                # direct import of deprecated function
                self.add_message(
                    "deprecated-task-script-util-datetime-parser-import", node=node
                )

            # keep track of relevant aliases to check individual calls later
            full_module_name = f"{node.modname}.{name}"
            if alias:
                self._ts_task_script_util_imports[alias] = full_module_name
            else:
                self._ts_task_script_util_imports[name] = full_module_name


def register(linter: PyLinter) -> None:
    """Enable loading this plugin."""
    linter.register_checker(ContextAPIDeprecationChecker(linter))
    linter.register_checker(TaskScriptUtilDeprecationChecker(linter))
