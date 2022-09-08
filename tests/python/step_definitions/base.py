import json
import os
from functools import partial
from pathlib import Path
from typing import Optional

import pytest
from pytest_bdd import given, parsers, then, when

from dotmodules.modules.modules import Modules
from dotmodules.settings import Settings

EXTRA_TYPES = {
    "P": Path,
    "S": str,
    "I": int,
}

p = partial(parsers.cfparse, extra_types=EXTRA_TYPES)


class ScenarioError(Exception):
    """Exception raised on invalid scenario definitions."""


@pytest.fixture
def settings() -> Settings:
    return Settings()


class ExecutionContext:
    def __init__(
        self, modules: Optional[Modules] = None, exception: Optional[Exception] = None
    ) -> None:
        if modules is None and exception is None:
            raise ValueError(
                "You have to instantiate the ExecutionConext with a modules object or "
                "an exception. You cannot omit both!"
            )

        self._modules = modules
        self._exception = exception

    @property
    def modules(self) -> Modules:
        if self._exception:
            raise self._exception
        return self._modules

    def match_error_message(self, error_message: str) -> None:
        assert self._exception is not None
        assert error_message in str(self._exception)
