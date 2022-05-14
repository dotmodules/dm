from pathlib import Path

import pytest

from dotmodules.modules import Module, ShellScriptHook


@pytest.fixture
def module() -> Module:
    module = Module(
        name="dummy_module",
        version="dummy_version",
        enabled=True,
        documentation=[""],
        variables={},
        root=Path(__file__).parent / "hook_testing_assets",
    )
    return module


class TestShellScriptHookPathHandling:
    def test__full_path_to_file_can_be_resolved(self, module: Module) -> None:
        hook = ShellScriptHook(
            path_to_script="./dummy_file.txt",
        )
        module.add_hook(hook=hook)

        assert hook.full_path_to_script

    def test__non_existing__path_to_file__error(self, module: Module) -> None:
        hook = ShellScriptHook(
            path_to_script="./non_existent_file",
        )
        module.add_hook(hook=hook)

        with pytest.raises(ValueError) as e:
            hook.full_path_to_script
        expected = "Hook.path_to_script does not name a file: './non_existent_file'"
        assert str(e.value) == expected
