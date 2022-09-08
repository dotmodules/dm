from pytest_bdd import then

from ..base import ExecutionContext, p, settings


@then(p('the module at index "{index:I}" should have its name set to "{name:S}"'))
def assert_module_name_at_index(
    execution_context: ExecutionContext, index: int, name: str
) -> None:
    modules = execution_context.modules
    module = modules[index - 1]
    assert module.name == name
