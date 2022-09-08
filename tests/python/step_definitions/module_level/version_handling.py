from pytest_bdd import then

from ..base import ExecutionContext, p, settings


@then(p('the module at index "{index:I}" should have its version set to "{version:S}"'))
def assert_module_version_at_index(
    execution_context: ExecutionContext, index: int, version: str
) -> None:
    modules = execution_context.modules
    module = modules[index - 1]
    assert module.version == version
