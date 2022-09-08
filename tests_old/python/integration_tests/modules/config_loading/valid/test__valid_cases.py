from pathlib import Path
from typing import cast

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.hooks import (
    LinkCleanUpHook,
    LinkDeploymentHook,
    ShellScriptHook,
)
from dotmodules.modules.modules import Module, Modules


@pytest.fixture
def modules(mocker: MockerFixture) -> Modules:
    mock_modules = mocker.MagicMock()
    return cast(Modules, mock_modules)


@pytest.mark.integration
class TestEndToEndValidConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent

    def test__full__without_deployment_target(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "full_with_global_enabled_section.toml"
        module = Module.from_path(path=file_path, deployment_target="", modules=modules)

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == [
            "line 1",
            " line 2",
            "  line 3",
        ]
        assert module.aggregated_variables == {
            "VAR_1": ["var1"],
            "VAR_2": ["var21", "var22", "var23"],
        }

        # =====================================================================
        #  Assert links
        # =====================================================================

        assert len(module.links) == 2

        link = module.links[0]
        assert link.name == "link_name_1"
        assert link.path_to_target == "path_to_target_1"
        assert link.path_to_symlink == "path_to_symlink_1"

        link = module.links[1]
        assert link.name == "link_name_2"
        assert link.path_to_target == "path_to_target_2"
        assert link.path_to_symlink == "path_to_symlink_2"

        # =====================================================================
        #  Assert top level hooks
        # =====================================================================

        assert len(module.hooks) == 4
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

        # =====================================================================
        #  Assert shell script hooks
        # =====================================================================

        shell_script_hooks = [
            hook for hook in module.hooks if hook.__class__ == ShellScriptHook
        ]
        assert len(shell_script_hooks) == 2
        hook = shell_script_hooks[0]
        assert hook.hook_name == "hook_name_1"
        assert hook.hook_priority == 1
        assert (
            hook.hook_description
            == "Runs local script <<UNDERLINE>>path_to_script_1<<RESET>>"
        )

        hook = shell_script_hooks[1]
        assert hook.hook_name == "hook_name_2"
        assert hook.hook_priority == 2
        assert (
            hook.hook_description
            == "Runs local script <<UNDERLINE>>path_to_script_2<<RESET>>"
        )

        # =====================================================================
        #  Assert link deployment hooks
        # =====================================================================

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkDeploymentHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "DEPLOY_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Deploys 2 links"
        assert hook.links == module.links

        # =====================================================================
        #  Assert link cleanup hooks
        # =====================================================================

        link_cleanup_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_cleanup_hooks) == 1
        hook = cast(LinkDeploymentHook, link_cleanup_hooks[0])
        assert hook.hook_name == "CLEAN_UP_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Cleans up 2 links"
        assert hook.links == module.links

        # =====================================================================
        #  Assert variable status hooks
        # =====================================================================

        assert len(module.variable_status_hooks) == 2

        hook = module.variable_status_hooks[0]
        assert hook.variable_name == "variable_name_1"
        assert hook.path_to_script == "path_to_script_1"
        assert hook.hook_name == "VARIABLE_STATUS_HOOK[variable_name_1]"
        assert hook.hook_priority == 0
        assert hook.hook_description == (
            "Retrieves deployment statistics for variable 'variable_name_1' "
            "through script <<UNDERLINE>>path_to_script_1<<RESET>>"
        )

        hook = module.variable_status_hooks[1]
        assert hook.variable_name == "variable_name_2"
        assert hook.path_to_script == "path_to_script_2"
        assert hook.hook_name == "VARIABLE_STATUS_HOOK[variable_name_2]"
        assert hook.hook_priority == 0
        assert hook.hook_description == (
            "Retrieves deployment statistics for variable 'variable_name_2' "
            "through script <<UNDERLINE>>path_to_script_2<<RESET>>"
        )

    def test__full__with_deployment_target(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "full_with_separated_enabled_section.toml"
        module = Module.from_path(
            path=file_path, deployment_target="my_target_1", modules=modules
        )

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == [
            "line 1",
            " line 2",
            "  line 3",
            "",
            "Target specific: my_target_1",
        ]
        assert module.aggregated_variables == {
            "VAR_1": ["var1"],
            "VAR_2": ["var21", "var22", "var23"],
            "VAR_3": ["var31", "var32", "var33"],
        }

        # =====================================================================
        #  Assert links
        # =====================================================================

        assert len(module.links) == 3

        link = module.links[0]
        assert link.name == "link_name_1"
        assert link.path_to_target == "path_to_target_1"
        assert link.path_to_symlink == "path_to_symlink_1"

        link = module.links[1]
        assert link.name == "link_name_2"
        assert link.path_to_target == "path_to_target_2"
        assert link.path_to_symlink == "path_to_symlink_2"

        link = module.links[2]
        assert link.name == "link_name_3"
        assert link.path_to_target == "path_to_target_3"
        assert link.path_to_symlink == "path_to_symlink_3"

        # =====================================================================
        #  Assert top level hooks
        # =====================================================================

        assert len(module.hooks) == 5
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

        # =====================================================================
        #  Assert shell script hooks
        # =====================================================================

        shell_script_hooks = [
            hook for hook in module.hooks if hook.__class__ == ShellScriptHook
        ]
        assert len(shell_script_hooks) == 3

        hook = shell_script_hooks[0]
        assert hook.hook_name == "hook_name_1"
        assert hook.hook_priority == 1
        assert (
            hook.hook_description
            == "Runs local script <<UNDERLINE>>path_to_script_1<<RESET>>"
        )

        hook = shell_script_hooks[1]
        assert hook.hook_name == "hook_name_2"
        assert hook.hook_priority == 2
        assert (
            hook.hook_description
            == "Runs local script <<UNDERLINE>>path_to_script_2<<RESET>>"
        )

        hook = shell_script_hooks[2]
        assert hook.hook_name == "hook_name_3"
        assert hook.hook_priority == 3
        assert (
            hook.hook_description
            == "Runs local script <<UNDERLINE>>path_to_script_3<<RESET>>"
        )

        # =====================================================================
        #  Assert link deployment hooks
        # =====================================================================

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkDeploymentHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "DEPLOY_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Deploys 3 links"
        assert hook.links == module.links

        # =====================================================================
        #  Assert link cleanup hooks
        # =====================================================================

        link_cleanup_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_cleanup_hooks) == 1
        hook = cast(LinkDeploymentHook, link_cleanup_hooks[0])
        assert hook.hook_name == "CLEAN_UP_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Cleans up 3 links"
        assert hook.links == module.links

        # =====================================================================
        #  Assert variable status hooks
        # =====================================================================

        assert len(module.variable_status_hooks) == 3

        hook = module.variable_status_hooks[0]
        assert hook.variable_name == "variable_name_1"
        assert hook.path_to_script == "path_to_script_1"
        assert hook.hook_name == "VARIABLE_STATUS_HOOK[variable_name_1]"
        assert hook.hook_priority == 0
        assert hook.hook_description == (
            "Retrieves deployment statistics for variable 'variable_name_1' "
            "through script <<UNDERLINE>>path_to_script_1<<RESET>>"
        )

        hook = module.variable_status_hooks[1]
        assert hook.variable_name == "variable_name_2"
        assert hook.path_to_script == "path_to_script_2"
        assert hook.hook_name == "VARIABLE_STATUS_HOOK[variable_name_2]"
        assert hook.hook_priority == 0
        assert hook.hook_description == (
            "Retrieves deployment statistics for variable 'variable_name_2' "
            "through script <<UNDERLINE>>path_to_script_2<<RESET>>"
        )

        hook = module.variable_status_hooks[2]
        assert hook.variable_name == "variable_name_3"
        assert hook.path_to_script == "path_to_script_3"
        assert hook.hook_name == "VARIABLE_STATUS_HOOK[variable_name_3]"
        assert hook.hook_priority == 0
        assert hook.hook_description == (
            "Retrieves deployment statistics for variable 'variable_name_3' "
            "through script <<UNDERLINE>>path_to_script_3<<RESET>>"
        )

    def test__minimal__without_deployment_target(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "minimal.toml"
        module = Module.from_path(path=file_path, deployment_target="", modules=modules)

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.aggregated_variables == {}
        assert module.links == []
        assert module.hooks == []
        assert module.variable_status_hooks == []

    def test__minimal__with_deployment_target(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "minimal.toml"
        # If there are no deployment target specific settings in the config, it
        # should ignore the deployment target loading silently.
        module = Module.from_path(
            path=file_path, deployment_target="my_target", modules=modules
        )

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.aggregated_variables == {}
        assert module.links == []
        assert module.hooks == []
        assert module.variable_status_hooks == []

    def test__empty_documetnation(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "empty_documentation.toml"
        module = Module.from_path(path=file_path, deployment_target="", modules=modules)

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.aggregated_variables == {}
        assert module.links == []
        assert module.hooks == []
        assert module.variable_status_hooks == []

    def test__empty_links(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "empty_links.toml"
        module = Module.from_path(path=file_path, deployment_target="", modules=modules)

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.aggregated_variables == {}
        assert module.links == []
        assert module.hooks == []
        assert module.variable_status_hooks == []

    def test__empty_shell_script_hooks(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "empty_shell_script_hooks.toml"
        module = Module.from_path(path=file_path, deployment_target="", modules=modules)

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.aggregated_variables == {}
        assert module.links == []
        assert module.hooks == []
        assert module.variable_status_hooks == []

    def test__empty_variable_status_hooks(self, modules: Modules) -> None:
        file_path = self.SAMPLE_FILE_DIR / "empty_variable_status_hooks.toml"
        module = Module.from_path(path=file_path, deployment_target="", modules=modules)

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.aggregated_variables == {}
        assert module.links == []
        assert module.hooks == []
        assert module.variable_status_hooks == []
