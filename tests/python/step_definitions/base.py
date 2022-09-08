from functools import partial
from pathlib import Path
from typing import Optional

from pytest_bdd import parsers

from dotmodules.modules.modules import Modules

EXTRA_TYPES = {
    "P": Path,
    "S": str,
    "I": int,
}

p = partial(parsers.cfparse, extra_types=EXTRA_TYPES)


class ScenarioError(Exception):
    """Exception raised on invalid scenario definitions."""


class ExecutionContext:
    def __init__(
        self, modules: Optional[Modules] = None, exception: Optional[Exception] = None
    ) -> None:
        if modules is None and exception is None:
            raise ValueError(
                "You have to instantiate the ExecutionConext with a modules object or "
                "an exception. You cannot omit both!"
            )

        # Explicit type narrowings becasue of mypy cannot understand exception raising.
        if modules is not None:
            self._modules = modules
        else:
            self._modules = None

        if exception is not None:
            self._exception = exception
        else:
            self._exception = None

    @property
    def modules(self) -> Modules:
        if self._exception:
            raise self._exception
        return self._modules

    def match_error_message(self, error_message: str) -> None:
        assert self._exception is not None
        assert error_message in str(self._exception)
