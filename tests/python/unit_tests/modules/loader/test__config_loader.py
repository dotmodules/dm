from pathlib import Path

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.loader import ConfigLoader, LoaderError, TomlLoader


class TestConfigLoaderInternals:
    def test__selecting_multiple_loaders_raises_error(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        class DummyLoader1:
            @staticmethod
            def can_load(config_file_path: Path) -> bool:
                # Returning constant true here to make this loader be selected.
                return True

        class DummyLoader2:
            @staticmethod
            def can_load(config_file_path: Path) -> bool:
                # Returning constant true here to make this loader be selected.
                return True

        mocker.patch(
            "dotmodules.modules.loader.ConfigLoader.__subclasses__",
            return_value=[DummyLoader1, DummyLoader2],
        )

        dummy_config_path = tmp_path / "dummy.config"
        dummy_config_path.touch()

        with pytest.raises(LoaderError) as error_context:
            ConfigLoader.get_loader_for_config_file(config_file_path=dummy_config_path)

        expected = rf"Multiple loaders \(DummyLoader1, DummyLoader2\) were selected for path '{dummy_config_path}'!"
        assert error_context.match(expected)


class TestTomlLoaderCases:
    def test__valid_toml_file_can_be_loaded(self, tmp_path: Path) -> None:
        config_file_path = tmp_path / "dummy.toml"
        with open(config_file_path, "w+") as f:
            f.write("variable = 42")

        loader = TomlLoader(config_file_path=config_file_path)

        result = loader.get(key="variable")
        assert result == 42

    def test__invalid_toml_file_should_raise_an_error(self, tmp_path: Path) -> None:
        config_file_path = tmp_path / "dummy.toml"
        with open(config_file_path, "w+") as f:
            f.write("this is not a valid toml syntax!!!")

        with pytest.raises(LoaderError) as error_context:
            TomlLoader(config_file_path=config_file_path)

        assert error_context.match("Toml loading error: .*")


class TestConfigLoaderEndToEndCases:
    def test__related_loader_can_be_selected(self, tmp_path: Path) -> None:
        config_file_path = tmp_path / "dummy.toml"
        with open(config_file_path, "w+") as f:
            f.write("variable = 42")

        loader = ConfigLoader.get_loader_for_config_file(
            config_file_path=config_file_path
        )

        assert loader.__class__ == TomlLoader

        result = loader.get(key="variable")
        assert result == 42

        with pytest.raises(LoaderError) as error_context:
            loader.get(key="non_existent_key")

        expected = "Cannot retrieve key 'non_existent_key'!"
        assert error_context.match(expected)
