from pytest_bdd import then, when

from dotmodules.modules.modules import Modules
from dotmodules.settings import Settings

from ..base import ExecutionContext, ScenarioError, p


@when("I run the dotmodules system", target_fixture="execution_context")
def load_the_dotmodules_system(settings: Settings) -> ExecutionContext:
    try:
        modules = Modules(settings=settings)
        return ExecutionContext(modules=modules)
    except Exception as e:
        return ExecutionContext(exception=e)


@then("there should be no modules loaded")
@then("there should be no loaded modules")
def no_loaded_modules(execution_context: ExecutionContext) -> None:
    # If the modules object was created check if there are 0 modules loaded.
    if execution_context._modules is not None:
        assert len(execution_context.modules) == 0


@then(p('there should be "{count:I}" loaded module'))
@then(p('there should be "{count:I}" loaded modules'))
def count_loaded_modules(execution_context: ExecutionContext, count: int) -> None:
    if count < 1:
        raise ScenarioError("You can only check if there is at least one loaded module")

    modules = execution_context.modules
    assert len(modules) == count


@then(p("a global error should have been raised:\n{error_message:S}"))
def global_error_should_have_been_raised(
    execution_context: ExecutionContext, error_message: str
) -> None:
    execution_context.match_error_message(error_message=error_message)
