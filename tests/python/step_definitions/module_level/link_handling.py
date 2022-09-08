from pytest_bdd import then

from ..base import ExecutionContext, p


@then(p('the module at index "{index:I}" should have "{count:I}" link registered'))
@then(p('the module at index "{index:I}" should have "{count:I}" links registered'))
def assert_module_has_link_count(
    execution_context: ExecutionContext, index: int, count: int
) -> None:
    modules = execution_context.modules
    module = modules[index - 1]
    assert len(module.links) == count


@then("there should be no module level errors")
def assert_no_module_level_errors(execution_context: ExecutionContext) -> None:
    modules = execution_context.modules
    for module in modules:
        assert not module.errors


@then(p('there should be no module level errors for module at index "{index:I}"'))
def assert_no_module_level_errors_for_module_at_index(
    execution_context: ExecutionContext, index: int
) -> None:
    modules = execution_context.modules
    module = modules[index - 1]
    assert not module.errors


@then(
    p('there should be a module level error for module at index "{index:I}":\n{errors}')
)
@then(
    p('there should be module level errors for module at index "{index:I}":\n{errors}')
)
def assert_module_level_errors_for_module_at_index(
    execution_context: ExecutionContext, index: int, errors: str
) -> None:
    error_list = errors.splitlines()

    modules = execution_context.modules
    module = modules[index - 1]
    for error in error_list:
        assert error in module.errors
