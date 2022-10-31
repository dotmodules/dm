from pytest_bdd import then

from ....base import ExecutionContext, p


@then(p('the module at index "{index:I}" should be enabled'))
def assert_module_enabled_at_index(context: ExecutionContext, index: int) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.enabled is True


@then(p('the module at index "{index:I}" should be disabled'))
def assert_module_disabled_at_index(context: ExecutionContext, index: int) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.enabled is False
