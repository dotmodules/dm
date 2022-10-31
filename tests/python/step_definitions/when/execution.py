from pytest_bdd import when

from dotmodules.modules.modules import Modules
from dotmodules.settings import Settings

from ..base import ExecutionContext, FailedContext, SucceededContext

# ============================================================================
#  DOTMODULES SYSTEM LOADING
# ============================================================================


@when("I run the dotmodules system", target_fixture="context")
def load_the_dotmodules_system(settings: Settings) -> ExecutionContext:
    try:
        modules = Modules(settings=settings)
        return SucceededContext(modules=modules)
    except Exception as e:
        return FailedContext(exception=e)
