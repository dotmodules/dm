from pytest_bdd import then

from ....base import ExecutionContext, p


@then(p('the module at index "{index:I}" should have its name set to "{name:S}"'))
def assert_module_name_at_index(
    context: ExecutionContext, index: int, name: str
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.name == name
