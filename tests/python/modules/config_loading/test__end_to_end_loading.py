from pathlib import Path
from typing import cast

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.hooks import (
    LinkCleanUpHook,
    LinkDeploymentHook,
    ShellScriptHook,
)
from dotmodules.modules.modules import Module, ModuleError, Modules


@pytest.mark.integration
class TestEndToEndConfigParsingCases:
    SAMPLE_FILE_DIR = Path(__file__).parent / "sample_config_files"

    def test__valid_file__full(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "valid__full.toml"
        module = Module.from_path(path=file_path)

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

    def test__valid_file__minimal(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "valid__minimal.toml"
        module = Module.from_path(path=file_path)

        assert module.name == "name_1"
        assert module.version == "version_1"
        assert module.variables == {}
        assert module.links == []
        assert module.hooks == []

    def test__invalid_file__non_existent_file(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "NON_EXISTENT"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = f"Configuration loading error: Config file at path '{file_path}' does not exist!"
        assert str(exception_info.value) == expected

    def test__invalid_file__toml_syntax(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__toml_syntax.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration loading error: Toml loading error: "
            "Found tokens after a closed string. Invalid TOML. (line 1 column 1 char 0)"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__name_missing(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__name_missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = "Configuration syntax error: Mandatory 'name' section is missing!"
        assert str(exception_info.value) == expected

    def test__invalid_file__name_empty(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__name_empty.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = "Configuration syntax error: Empty value for section 'name'!"
        assert str(exception_info.value) == expected

    def test__invalid_file__name_non_string(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__name_non_string.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Value for section 'name' should be a string, "
            "got '['I am not a string']'!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__version_missing(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__version_missing.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = "Configuration syntax error: Mandatory 'version' section is missing!"
        assert str(exception_info.value) == expected

    def test__invalid_file__version_empty(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__version_empty.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = "Configuration syntax error: Empty value for section 'version'!"
        assert str(exception_info.value) == expected

    def test__invalid_file__version_non_string(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__version_non_string.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Value for section 'version' "
            "should be a string, got '['I am not a string']'!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__variables_structure(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__variables_structure.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: The 'variables' section should have the "
            "following syntax: 'VARIABLE_NAME' = ['var_1', 'var_2', ..] !"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__links_missing_mandatory_field_1(self) -> None:
        file_path = (
            self.SAMPLE_FILE_DIR / "invalid__link_missing_mandatory_field_1.toml"
        )
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Missing mandatory field 'name' from section 'links' "
            "item at index 1!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__links_missing_mandatory_field_2(self) -> None:
        file_path = (
            self.SAMPLE_FILE_DIR / "invalid__link_missing_mandatory_field_2.toml"
        )
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Missing mandatory field 'path_to_target' from section "
            "'links' item at index 1!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__links_missing_mandatory_field_3(self) -> None:
        file_path = (
            self.SAMPLE_FILE_DIR / "invalid__link_missing_mandatory_field_3.toml"
        )
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Missing mandatory field 'path_to_symlink' from section "
            "'links' item at index 1!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__links_additional_field(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__link_additional_field.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Unexpected field 'additional_field' found for section "
            "'links' item at index 1!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__links_additional_fields(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__link_additional_fields.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Unexpected fields 'additional_field_1', "
            "'additional_field_2' found for section 'links' item at index 1!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__hooks_missing_mandatory_field_1(self) -> None:
        file_path = (
            self.SAMPLE_FILE_DIR / "invalid__hook_missing_mandatory_field_1.toml"
        )
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Missing mandatory field 'name' from section 'hooks' "
            "item at index 2!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__hooks_missing_mandatory_field_2(self) -> None:
        file_path = (
            self.SAMPLE_FILE_DIR / "invalid__hook_missing_mandatory_field_2.toml"
        )
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Missing mandatory field 'path_to_script' from section "
            "'hooks' item at index 2!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__hooks_missing_mandatory_field_3(self) -> None:
        file_path = (
            self.SAMPLE_FILE_DIR / "invalid__hook_missing_mandatory_field_3.toml"
        )
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Missing mandatory field 'priority' from section "
            "'hooks' item at index 2!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__hooks_additional_field(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__hook_additional_field.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Unexpected field 'additional_field' found for section "
            "'hooks' item at index 2!"
        )
        assert str(exception_info.value) == expected

    def test__invalid_file__hooks_additional_fields(self) -> None:
        file_path = self.SAMPLE_FILE_DIR / "invalid__hook_additional_fields.toml"
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = (
            "Configuration syntax error: Unexpected fields 'additional_field_1', "
            "'additional_field_2' found for section 'hooks' item at index 2!"
        )
        assert str(exception_info.value) == expected

    def test__unexpected_error_can_be_handled(self, mocker: MockerFixture) -> None:
        file_path = self.SAMPLE_FILE_DIR / "irrelevant_file.toml"
        mocker.patch(
            "dotmodules.modules.loader.ConfigLoader.get_loader_for_config_file"
        )
        mocker.patch(
            "dotmodules.modules.parser.ConfigParser.parse_name",
            side_effect=Exception("shit happens"),
        )
        with pytest.raises(ModuleError) as exception_info:
            Module.from_path(path=file_path)
        expected = "Unexpected error happened during module loading: shit happens"
        assert str(exception_info.value) == expected


@pytest.mark.integration
class TestEndToEndModuleLoadingCases:
    def test__modules_can_be_loaded_from_a_directory_structure(self) -> None:
        modules_root_path = Path(__file__).parent / "dummy_modules_dir"
        config_file_name = "config.toml"
        modules = Modules.load(
            modules_root_path=modules_root_path, config_file_name=config_file_name
        )
        assert modules
        assert len(modules) == 4

        # Modules are sorted by root:
        # .../category_1/module_2  [enabled]
        # .../category_1/module_3  [enabled]
        # .../category_1/module_4  [disabled]
        # .../module_1  [enabled]

        # =====================================================================
        # MODULE 2

        module = modules.modules[0]
        assert isinstance(module, Module)
        assert module.name == "module_2"
        assert module.version == "version_2"
        assert module.enabled
        assert module.documentation == ["docs_2"]
        assert module.variables == {
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

        module = modules.modules[1]
        assert isinstance(module, Module)
        assert module.name == "module_3"
        assert module.version == "version_3"
        assert module.enabled
        assert module.documentation == ["docs_3"]
        assert module.variables == {
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

        module = modules.modules[2]
        assert isinstance(module, Module)
        assert module.name == "module_4"
        assert module.version == "version_4"
        assert not module.enabled
        assert module.documentation == ["docs_4"]
        assert module.variables == {
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

        module = modules.modules[3]
        assert isinstance(module, Module)
        assert module.name == "module_1"
        assert module.version == "version_1"
        assert module.enabled
        assert module.documentation == ["docs_1"]
        assert module.variables == {
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

    def test__error_during_loading(self) -> None:
        modules_root_path = Path(__file__).parent / "dummy_modules_dir_error"
        config_file_name = "config.toml"
        with pytest.raises(ModuleError) as exception_info:
            Modules.load(
                modules_root_path=modules_root_path, config_file_name=config_file_name
            )
        failed_module_path = (
            modules_root_path / "category_1" / "module_3" / "config.toml"
        )
        expected = (
            f"Error while loading module at path '{failed_module_path}': "
            "Configuration syntax error: Missing mandatory field 'name' from section "
            "'links' item at index 1!"
        )
        assert str(exception_info.value) == expected
