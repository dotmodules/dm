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
class TestInvalidNameConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent

    def test__name_missing(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "name_missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = "Configuration syntax error: Mandatory 'name' section is missing!"
        assert exception_info.match(expected)

    def test__name_empty(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "name_empty.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = "Configuration syntax error: Empty value for section 'name'!"
        assert exception_info.match(expected)

    def test__name_non_string(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "name_non_string.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path, deployment_target="", modules=modules)
        expected = (
            "Configuration syntax error: Value for section 'name' should be a string, "
            "got list!"
        )
        assert exception_info.match(expected)
