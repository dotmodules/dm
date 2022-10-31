from pytest_bdd import then

from ....base import ExecutionContext, p


@then(p('the module at index "{index:I}" should have its version set to "{version:S}"'))
def assert_module_version_at_index(
    context: ExecutionContext, index: int, version: str
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.version == version
