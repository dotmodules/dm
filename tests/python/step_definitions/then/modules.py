from pathlib import Path

from pytest_bdd import then

from ..base import ExecutionContext, ScenarioError, p

# ============================================================================
#  LOADED MODULES
# ============================================================================


@then("there should be no modules loaded")
@then("there should be no loaded modules")
def no_loaded_modules(context: ExecutionContext) -> None:
    # If the modules object was created check if there are 0 modules loaded.
    if context.succeeded:
        assert len(context.modules) == 0


@then(p('there should be "{count:I}" loaded module'))
@then(p('there should be "{count:I}" loaded modules'))
def count_loaded_modules(context: ExecutionContext, count: int) -> None:
    if count < 1:
        raise ScenarioError("You can only check if there is at least one loaded module")

    modules = context.modules
    assert len(modules) == count


@then(p("a global error should have been raised:\n{error_message:S}"))
def global_error_should_have_been_raised(
    context: ExecutionContext, error_message: str
) -> None:
    context.match_error_message(error_message=error_message)


# ============================================================================
#  MODULE ROOTS
# ============================================================================


@then(p("the modules should have the following relative roots:\n{roots:S}"))
def assert_module_roots(context: ExecutionContext, roots: str, tmp_path: Path) -> None:
    root_items = roots.splitlines()
    if len(root_items) != len(set(root_items)):
        raise ScenarioError("Given roots should be unique!")

    modules = context.modules
    assert len(modules) == len(root_items)

    module_absolute_roots = [module.root for module in modules]

    for relative_root in root_items:
        absolute_root = tmp_path / relative_root
        assert absolute_root in module_absolute_roots


@then(p("the modules should have the following relative roots in order:\n{roots:S}"))
def assert_module_roots_in_order(
    context: ExecutionContext, roots: str, tmp_path: Path
) -> None:
    root_items = roots.splitlines()
    if len(root_items) != len(set(root_items)):
        raise ScenarioError("Given roots should be unique!")

    modules = context.modules
    assert len(modules) == len(root_items)

    module_absolute_roots = [module.root for module in modules]

    for module_absolute_root, relative_root in zip(module_absolute_roots, root_items):
        absolute_root = tmp_path / relative_root
        assert absolute_root == module_absolute_root
