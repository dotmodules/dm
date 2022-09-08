import pytest

from dotmodules.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings()


# NOTE: Since pytest-pdd is based on decorated function and the decorated
# function names are generated dynamically and assigned to the current
# stackframe local scope, unfortunately we cannot do better than a star import
# if we want to break up the step definitions into multiple files to avoind a
# gigantic conftest file.. More details on this:
# https://github.com/pytest-dev/pytest-bdd/blob/master/src/pytest_bdd/steps.py#L176

# Ignoring flake8 errors:
# E402 module level import not at top of file
#   The 'settings' fixture has to be already available for the step definitons
#   on load time.
# F401 '.step_definitions.*' imported but unused
#   pytest will make the loaded objects available globally
# F403 'from .step_definitions import *' used; unable to detect undefined names
#   We have to use star import here unfortunately..
from .step_definitions import *  # noqa: E402 F401, F403
