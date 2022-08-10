from pathlib import Path
from typing import cast

import pytest

from dotmodules.modules.hooks import (
    LinkCleanUpHook,
    LinkDeploymentHook,
    ShellScriptHook,
)
from dotmodules.modules.modules import Module


@pytest.mark.integration
class TestEndToEndValidConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent

    def test__full__without_deployment_target(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "full_with_global_enabled_section.toml"
        module = Module.from_path(path=file_path, deployment_target="")

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == [
            "line 1",
            " line 2",
            "  line 3",
        ]
        assert module.variables == {
            "VAR_1": ["var1"],
            "VAR_2": ["var21", "var22", "var23"],
        }

        assert len(module.links) == 2

        link = module.links[0]
        assert link.name == "link_name_1"
        assert link.path_to_target == "path_to_target_1"
        assert link.path_to_symlink == "path_to_symlink_1"

        link = module.links[1]
        assert link.name == "link_name_2"
        assert link.path_to_target == "path_to_target_2"
        assert link.path_to_symlink == "path_to_symlink_2"

        assert len(module.hooks) == 4
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

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

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkDeploymentHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "DEPLOY_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Deploys 2 links"
        assert hook.links == module.links

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "CLEAN_UP_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Cleans up 2 links"
        assert hook.links == module.links

    def test__full__with_deployment_target(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "full_with_separated_enabled_section.toml"
        module = Module.from_path(path=file_path, deployment_target="my_target_1")

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == [
            "line 1",
            " line 2",
            "  line 3",
            "",
            "Target specific: my_target_1",
        ]
        assert module.variables == {
            "VAR_1": ["var1"],
            "VAR_2": ["var21", "var22", "var23"],
            "VAR_3": ["var31", "var32", "var33"],
        }

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

        assert len(module.hooks) == 5
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

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

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkDeploymentHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "DEPLOY_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Deploys 3 links"
        assert hook.links == module.links

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "CLEAN_UP_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Cleans up 3 links"
        assert hook.links == module.links

    def test__minimal__without_deployment_target(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "minimal.toml"
        module = Module.from_path(path=file_path, deployment_target="")

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.variables == {}
        assert module.links == []
        assert module.hooks == []

    def test__minimal__with_deployment_target(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "minimal.toml"
        # If there are no deployment target specific settings in the config, it
        # should ignore the deployment target loading silently.
        module = Module.from_path(path=file_path, deployment_target="my_target")

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.variables == {}
        assert module.links == []
        assert module.hooks == []

    def test__empty_documetnation(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "empty_documentation.toml"
        module = Module.from_path(path=file_path, deployment_target="")

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.variables == {}
        assert module.links == []
        assert module.hooks == []

    def test__empty_links(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "empty_links.toml"
        module = Module.from_path(path=file_path, deployment_target="")

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.variables == {}
        assert module.links == []
        assert module.hooks == []

    def test__empty_hooks(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "empty_hooks.toml"
        module = Module.from_path(path=file_path, deployment_target="")

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.version == "version_1"
        assert module.documentation == []
        assert module.variables == {}
        assert module.links == []
        assert module.hooks == []
