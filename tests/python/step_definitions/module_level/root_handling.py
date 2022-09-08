from pathlib import Path

from pytest_bdd import then

from ..base import ExecutionContext, ScenarioError, p


@then(p("the modules should have the following relative roots:\n{roots:S}"))
def assert_module_roots(
    execution_context: ExecutionContext, roots: str, tmp_path: Path
) -> None:
    root_items = roots.splitlines()
    if len(root_items) != len(set(root_items)):
        raise ScenarioError("Given roots should be unique!")

    modules = execution_context.modules
    assert len(modules) == len(root_items)

    module_absolute_roots = [module.root for module in modules]

    for relative_root in root_items:
        absolute_root = tmp_path / relative_root
        assert absolute_root in module_absolute_roots


@then(p("the modules should have the following relative roots in order:\n{roots:S}"))
def assert_module_roots_in_order(
    execution_context: ExecutionContext, roots: str, tmp_path: Path
) -> None:
    root_items = roots.splitlines()
    if len(root_items) != len(set(root_items)):
        raise ScenarioError("Given roots should be unique!")

    modules = execution_context.modules
    assert len(modules) == len(root_items)

    module_absolute_roots = [module.root for module in modules]

    for module_absolute_root, relative_root in zip(module_absolute_roots, root_items):
        absolute_root = tmp_path / relative_root
        assert absolute_root == module_absolute_root
