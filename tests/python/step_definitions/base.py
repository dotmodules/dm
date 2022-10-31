from abc import ABC, abstractmethod, abstractproperty
from functools import partial
from pathlib import Path

from pytest_bdd import parsers

from dotmodules.modules.modules import Modules

# ============================================================================
#  EXECUTION CONTEXT HANDLING
# ============================================================================

EXTRA_TYPES = {
    "P": Path,
    "S": str,
    "I": int,
}

p = partial(parsers.cfparse, extra_types=EXTRA_TYPES)

# ============================================================================
#  SCENARIO BUILDING ERROR
# ============================================================================


class ScenarioError(Exception):
    """Exception raised on invalid scenario definitions."""


# ============================================================================
#  EXECUTION CONTEXT HANDLING
# ============================================================================


class ExecutionContext(ABC):
    @abstractproperty
    def succeeded(self) -> bool:
        """Returns if the execution was successful or not"""

    @abstractproperty
    def modules(self) -> Modules:
        """It should return the executed module obejct or raise the captured error."""

    @abstractmethod
    def match_error_message(self, error_message: str) -> None:
        """It should match an error message if the executoin failed"""


class SucceededContext(ExecutionContext):
    def __init__(self, modules: Modules) -> None:
        self._modules = modules

    @property
    def succeeded(self) -> bool:
        return True

    @property
    def modules(self) -> Modules:
        return self._modules

    def match_error_message(self, error_message: str) -> None:
        raise ScenarioError("SucceededContext cannot match error message")


class FailedContext(ExecutionContext):
    def __init__(self, exception: Exception) -> None:
        self._exception = exception

    @property
    def succeeded(self) -> bool:
        return False

    @property
    def modules(self) -> Modules:
        raise self._exception

    def match_error_message(self, error_message: str) -> None:
        assert self._exception is not None
        assert error_message in str(self._exception)
