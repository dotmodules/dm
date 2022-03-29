from pathlib import Path

from dotmodules.settings import load_settings


class TestSettings:
    def test__settings_can_be_parsed(self):
        dummy_args = []
        dummy_args += ["--debug", "0"]
        dummy_args += ["--relative-modules-path", "my/relative/modules/path"]
        dummy_args += ["--config-file-name", "my-config-file-name"]
        dummy_args += ["--text-wrap-limit", "90"]
        dummy_args += ["--indent", "4"]
        dummy_args += ["--prompt-template", "my-prompt-template"]
        dummy_args += ["--hotkey-exit", "my-hotkey-exit"]
        dummy_args += ["--hotkey-help", "my-hotkey-help"]
        dummy_args += ["--hotkey-hooks", "my-hotkey-hooks"]
        dummy_args += ["--hotkey-modules", "my-hotkey-modules"]
        dummy_args += ["--hotkey-variables", "my-hotkey-variables"]
        dummy_args += ["--warning-wrapped-docs", "0"]

        load_settings(args=dummy_args)

        # Importing the singleton-like 'settings' variable.
        from dotmodules.settings import settings

        assert settings.debug == 0
        assert settings.relative_modules_path == Path("my/relative/modules/path")
        assert settings.config_file_name == "my-config-file-name"
        assert settings.text_wrap_limit == 90
        assert settings.indent == 4
        assert settings.prompt_template == "my-prompt-template"
        assert settings.hotkey_exit == "my-hotkey-exit"
        assert settings.hotkey_help == "my-hotkey-help"
        assert settings.hotkey_hooks == "my-hotkey-hooks"
        assert settings.hotkey_modules == "my-hotkey-modules"
        assert settings.hotkey_variables == "my-hotkey-variables"
        assert settings.warning_wrapped_docs == 0
