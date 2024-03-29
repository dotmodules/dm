from pathlib import Path
from typing import cast

import pytest

from dotmodules.modules.hooks import (
    LinkCleanUpHook,
    LinkDeploymentHook,
    ShellScriptHook,
)
from dotmodules.modules.modules import Module, ModuleError, Modules
from dotmodules.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.mark.integration
class TestEndToEndModuleLoadingCases:
    def test__modules_can_be_loaded_from_a_directory_structure(
        self, settings: Settings
    ) -> None:
        settings.relative_modules_path = Path(__file__).parent / "dummy_modules_dir"
        settings.config_file_name = "dm.toml"
        settings.deployment_target = ""
        settings.dm_cache_root = Path("/my/dm/cache/root")
        settings.dm_cache_variables = Path("/my/dm/cache/variables")
        settings.indent = "my_indent"
        settings.text_wrap_limit = 42

        modules = Modules(settings=settings)
        assert modules
        assert len(modules) == 4

        # Modules are sorted by root:
        # .../category_1/module_2  [enabled]
        # .../category_1/module_3  [enabled]
        # .../category_1/module_4  [disabled]
        # .../module_1  [enabled]

        # =====================================================================
        # MODULE 2

        module = modules[0]
        assert isinstance(module, Module)
        assert module.name == "module_2"
        assert module.version == "version_2"
        assert module.enabled
        assert module.documentation == ["docs_2"]
        assert module.aggregated_variables == {
            "VAR_2_1": ["var_1"],
            "VAR_2_2": ["var_2_1", "var_2_2", "var_2_3"],
        }
        assert len(module.links) == 1
        link = module.links[0]
        assert link.name == "link_name_2"
        assert link.path_to_target == "path_to_target_2"
        assert link.path_to_symlink == "path_to_symlink_2"

        assert len(module.hooks) == 3
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

        shell_script_hooks = [
            hook for hook in module.hooks if hook.__class__ == ShellScriptHook
        ]
        assert len(shell_script_hooks) == 1
        hook = shell_script_hooks[0]
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
        assert hook.hook_description == "Deploys 1 link"
        assert hook.links == module.links

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "CLEAN_UP_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Cleans up 1 link"
        assert hook.links == module.links

        # =====================================================================
        # MODULE 3

        module = modules[1]
        assert isinstance(module, Module)
        assert module.name == "module_3"
        assert module.version == "version_3"
        assert module.enabled
        assert module.documentation == ["docs_3"]
        assert module.aggregated_variables == {
            "VAR_3_1": ["var_1"],
            "VAR_3_2": ["var_2_1", "var_2_2", "var_2_3"],
        }
        assert len(module.links) == 1
        link = module.links[0]
        assert link.name == "link_name_3"
        assert link.path_to_target == "path_to_target_3"
        assert link.path_to_symlink == "path_to_symlink_3"

        assert len(module.hooks) == 3
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

        shell_script_hooks = [
            hook for hook in module.hooks if hook.__class__ == ShellScriptHook
        ]
        assert len(shell_script_hooks) == 1
        hook = shell_script_hooks[0]
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
        assert hook.hook_description == "Deploys 1 link"
        assert hook.links == module.links

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "CLEAN_UP_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Cleans up 1 link"
        assert hook.links == module.links

        # =====================================================================
        # MODULE 4

        module = modules[2]
        assert isinstance(module, Module)
        assert module.name == "module_4"
        assert module.version == "version_4"
        assert not module.enabled
        assert module.documentation == ["docs_4"]
        assert module.aggregated_variables == {
            "VAR_4_1": ["var_1"],
            "VAR_4_2": ["var_2_1", "var_2_2", "var_2_3"],
        }
        assert len(module.links) == 1
        link = module.links[0]
        assert link.name == "link_name_4"
        assert link.path_to_target == "path_to_target_4"
        assert link.path_to_symlink == "path_to_symlink_4"

        assert len(module.hooks) == 3
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

        shell_script_hooks = [
            hook for hook in module.hooks if hook.__class__ == ShellScriptHook
        ]
        assert len(shell_script_hooks) == 1
        hook = shell_script_hooks[0]
        assert hook.hook_name == "hook_name_4"
        assert hook.hook_priority == 4
        assert (
            hook.hook_description
            == "Runs local script <<UNDERLINE>>path_to_script_4<<RESET>>"
        )

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkDeploymentHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "DEPLOY_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Deploys 1 link"
        assert hook.links == module.links

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "CLEAN_UP_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Cleans up 1 link"
        assert hook.links == module.links

        # =====================================================================
        # MODULE 1

        module = modules[3]
        assert isinstance(module, Module)
        assert module.name == "module_1"
        assert module.version == "version_1"
        assert module.enabled
        assert module.documentation == ["docs_1"]
        assert module.aggregated_variables == {
            "VAR_1_1": ["var_1"],
            "VAR_1_2": ["var_2_1", "var_2_2", "var_2_3"],
        }
        assert len(module.links) == 1
        link = module.links[0]
        assert link.name == "link_name_1"
        assert link.path_to_target == "path_to_target_1"
        assert link.path_to_symlink == "path_to_symlink_1"

        assert len(module.hooks) == 3
        assert set([ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]) == set(
            [hook.__class__ for hook in module.hooks]
        )

        shell_script_hooks = [
            hook for hook in module.hooks if hook.__class__ == ShellScriptHook
        ]
        assert len(shell_script_hooks) == 1
        hook = shell_script_hooks[0]
        assert hook.hook_name == "hook_name_1"
        assert hook.hook_priority == 1
        assert (
            hook.hook_description
            == "Runs local script <<UNDERLINE>>path_to_script_1<<RESET>>"
        )

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkDeploymentHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "DEPLOY_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Deploys 1 link"
        assert hook.links == module.links

        link_deployment_hooks = [
            hook for hook in module.hooks if hook.__class__ == LinkCleanUpHook
        ]
        assert len(link_deployment_hooks) == 1
        hook = cast(LinkDeploymentHook, link_deployment_hooks[0])
        assert hook.hook_name == "CLEAN_UP_LINKS"
        assert hook.hook_priority == 0
        assert hook.hook_description == "Cleans up 1 link"
        assert hook.links == module.links

    def test__error_during_loading(self, settings: Settings) -> None:
        settings.relative_modules_path = (
            Path(__file__).parent / "dummy_modules_dir_error"
        )
        settings.config_file_name = "dm.toml"
        settings.deployment_target = ""

        with pytest.raises(ModuleError) as exception_info:
            Modules(settings=settings)
        failed_module_path = (
            settings.relative_modules_path / "category_1" / "module_3" / "dm.toml"
        )
        expected = (
            f"Error while loading module at path '{failed_module_path}': "
            "Configuration syntax error: Missing mandatory field 'name' from section "
            "'links' item at index 1!"
        )
        assert str(exception_info.value) == expected
