from pathlib import Path
from typing import Any, List

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.settings import _get_argument_list, load_settings


class TestSettings:
    def test__settings_can_be_parsed(self, mocker: MockerFixture) -> None:
        dummy_args = []
        dummy_args += ["--debug", "1"]
        dummy_args += ["--deployment-target", "my-target"]
        dummy_args += ["--relative-modules-path", "my/relative/modules/path"]
        dummy_args += ["--config-file-name", "my-config-file-name"]
        dummy_args += ["--text-wrap-limit", "90"]
        dummy_args += ["--indent", "4"]
        dummy_args += ["--column-padding", "2"]
        dummy_args += ["--prompt-template", "my-prompt-template"]
        dummy_args += ["--hotkey-exit", "my-hotkey-exit"]
        dummy_args += ["--hotkey-help", "my-hotkey-help"]
        dummy_args += ["--hotkey-hooks", "my-hotkey-hooks"]
        dummy_args += ["--hotkey-modules", "my-hotkey-modules"]
        dummy_args += ["--hotkey-variables", "my-hotkey-variables"]
        dummy_args += ["--warning-wrapped-docs", "0"]

        mocker.patch("dotmodules.settings._get_argument_list", return_value=dummy_args)

        settings = load_settings()

        assert settings.debug is True
        assert settings.deployment_target == "my-target"
        assert settings.relative_modules_path == Path("my/relative/modules/path")
        assert settings.config_file_name == "my-config-file-name"
        assert settings.text_wrap_limit == 90
        assert settings.indent == "    "
        assert settings.column_padding == "  "
        assert settings.prompt_template == "my-prompt-template"
        assert settings.hotkey_exit == "my-hotkey-exit"
        assert settings.hotkey_help == "my-hotkey-help"
        assert settings.hotkey_hooks == "my-hotkey-hooks"
        assert settings.hotkey_modules == "my-hotkey-modules"
        assert settings.hotkey_variables == "my-hotkey-variables"
        assert settings.warning_wrapped_docs is False

        assert (
            settings.body_width
            == settings.text_wrap_limit
            - settings.header_width
            - len(settings.column_padding)
        )

    def test__error_during_parsing(self, mocker: MockerFixture) -> None:
        # Not passing any paramteres..
        dummy_args: List[Any] = []
        mocker.patch("dotmodules.settings._get_argument_list", return_value=dummy_args)

        with pytest.raises(SystemExit):
            load_settings()

    def test__parameters_can_be_loaded_from_sys(self, mocker: MockerFixture) -> None:
        dummy_args = [1, 2, 3, 4, 5]
        mocker.patch(
            "dotmodules.settings.sys.argv",
            new_callable=mocker.PropertyMock(return_value=dummy_args),
        )

        result = _get_argument_list()
        assert result == [2, 3, 4, 5]
