from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.loader import ConfigLoader
from dotmodules.modules.parser import ConfigParser


@pytest.fixture
def mock_loader(mocker: MockerFixture) -> MagicMock:
    # By default the type of a MagicMock object is Any. We want to narrow it
    # back to MagicMock..
    return cast(MagicMock, mocker.MagicMock())


@pytest.fixture
def parser(mock_loader: MagicMock) -> ConfigParser:
    loader = cast(ConfigLoader, mock_loader)
    return ConfigParser(loader=loader)
