from pathlib import Path

import pytest

from dotmodules.modules import HookItem


@pytest.fixture
def module_root():
    return Path(__file__).parent / "hook_testing_assets"


class TestLinkPathToFilePreparing:
    def test__full_path_to_file_can_be_resolved(self, module_root):
        hook = HookItem(
            path_to_script="./dummy_file.txt",
        )
        hook.module_root = module_root

        assert hook.full_path_to_script

    def test__non_existing__path_to_file__error(self, module_root):
        hook = HookItem(
            path_to_script="./non_existent_file",
        )
        hook.module_root = module_root

        with pytest.raises(ValueError) as e:
            hook.full_path_to_script
        expected = "Hook.path_to_script does not name a file: './non_existent_file'"
        assert str(e.value) == expected
