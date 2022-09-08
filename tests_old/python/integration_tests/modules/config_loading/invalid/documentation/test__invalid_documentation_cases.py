from pathlib import Path
from typing import cast

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.modules import Module, ModuleError, Modules


@pytest.fixture
def modules(mocker: MockerFixture) -> Modules:
    mock_modules = mocker.MagicMock()
    return cast(Modules, mock_modules)


@pytest.mark.integration
class TestInvalidDocumentationConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent

    def test__invalid_documentation_type(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid_documentation_type.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Value for section 'documentation' should be "
            "a string, got int!"
        )
        assert exception_info.match(expected)
