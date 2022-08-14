from pathlib import Path

from pytest_mock.plugin import MockerFixture

from dotmodules.modules.hooks import (
    HookAdapterScript,
    LinkCleanUpHook,
    LinkDeploymentHook,
    ShellScriptHook,
    VariableStatusHook,
)
from dotmodules.modules.links import LinkItem
from dotmodules.settings import Settings


class TestShellScriptHookArgumentBuildingCases:
    def test__shell_script_hook_can_build_its_arguments(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        # =========================================================================
        #  SETUP
        # =========================================================================

        # Module related dummy values.
        dummy_module_root = tmp_path
        dummy_module_name = "my_module_name"
        dummy_module = mocker.MagicMock()
        dummy_module.name = dummy_module_name
        dummy_module.root = dummy_module_root

        # Shell script hook related dummy values.
        dummy_path_to_script = "./dummy.script"
        dummy_hook_name = "my_hook_name"
        dummy_hook_priority = 42

        # Settings related dummy values and mocked items.
        dummy_cache_root = "my_cache_root"
        dummy_cache_variables = "my_cache_variables"
        dummy_indent = "my_indent"
        dummy_text_wrap_limit = 90
        dummy_settings = Settings()
        dummy_settings.dm_cache_root = Path(dummy_cache_root)
        dummy_settings.dm_cache_variables = Path(dummy_cache_variables)
        dummy_settings.indent = dummy_indent
        dummy_settings.text_wrap_limit = dummy_text_wrap_limit

        # Current working directory related mocked items.
        dummy_cwd = "my_cwd"
        mocker.patch("dotmodules.modules.hooks.os.getcwd", return_value=dummy_cwd)

        # Path manager related mocked items and dummy values.
        mock_path_manager = mocker.patch("dotmodules.modules.hooks.PathManager")
        # Single call mocking for the shell script hook path_to_script value.
        dummy_resolved_path_to_script = "my_resolved_path_to_script"
        mock_path_manager.return_value.resolve_local_path.return_value = (
            dummy_resolved_path_to_script
        )
        # Single call mocking for the hook adapter script absolute path resolving.
        dummy_resolved_hook_adapter_script = "my_resolved_hook_adapter_script"
        mock_path_manager.return_value.resolve_absolute_path.return_value = (
            dummy_resolved_hook_adapter_script
        )
        # Single relative path calculation for the relative dm repo root.
        dummy_relative_dm_repo_root = "my_relative_dm_repo_root"
        mock_path_manager.return_value.get_relative_path.return_value = (
            dummy_relative_dm_repo_root
        )

        # Shell adapter related dummy values and mocked items.
        dummy_status_code = 0
        mock_shell_adapter = mocker.patch("dotmodules.modules.hooks.ShellAdapter")
        mock_shell_adapter.return_value.execute_interactively.return_value = (
            dummy_status_code
        )

        # Assembly of the expected command as a list of string. This will be passed
        # to the shell adapter.
        expected_command = [
            # 0 - hook adapter script absolute path
            dummy_resolved_hook_adapter_script,
            # 1 - DM_REPO_ROOT
            dummy_relative_dm_repo_root,
            # 2 - dm__config__target_hook_name
            dummy_hook_name,
            # 3 - dm__config__target_hook_priority
            str(dummy_hook_priority),
            # 4 - dm__config__target_module_name
            dummy_module_name,
            # 5 - dm__config__dm_cache_root
            dummy_cache_root,
            # 6 - dm__config__dm_cache_variables
            dummy_cache_variables,
            # 7 - dm__config__indent
            str(dummy_indent),
            # 8 - dm__config__wrap_limit
            str(dummy_text_wrap_limit),
            # 9 - dm__config__target_hook_script
            dummy_resolved_path_to_script,
        ]

        # =========================================================================
        #  EXECUTION
        # =========================================================================

        hook = ShellScriptHook(
            path_to_script=dummy_path_to_script,
            name=dummy_hook_name,
            priority=dummy_hook_priority,
        )

        # To be able to execute the hook, its exeecution context needs to be
        # initialized from the corrrsponding module and from the settings
        # objects.
        hook.initialize_execution_context(module=dummy_module, settings=dummy_settings)
        result = hook.execute()

        # =========================================================================
        #  ASSERTION
        # =========================================================================

        assert result.status_code == dummy_status_code
        assert not result.execution_result

        # Shell adapter mocked call checking.
        mock_shell_adapter.return_value.execute_interactively.assert_called_with(
            command=expected_command, cwd=dummy_module_root
        )

        # Path manager mocked call checking.
        mock_path_manager.return_value.resolve_local_path.assert_called_with(
            dummy_path_to_script
        )
        mock_path_manager.return_value.resolve_absolute_path.assert_called_with(
            HookAdapterScript.SHELL_SCRIPT, resolve_symlinks=True
        )
        mock_path_manager.return_value.get_relative_path.assert_called_with(
            from_path=dummy_module_root, to_path=dummy_cwd
        )

    def test__link_deployment_hook_can_build_its_arguments(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        # =========================================================================
        #  SETUP
        # =========================================================================

        # Module related dummy values.
        dummy_module_root = tmp_path
        dummy_module_name = "my_module_name"
        dummy_module = mocker.MagicMock()
        dummy_module.name = dummy_module_name
        dummy_module.root = dummy_module_root

        # Settings related dummy values and mocked items.
        dummy_cache_root = "my_cache_root"
        dummy_cache_variables = "my_cache_variables"
        dummy_indent = "my_indent"
        dummy_text_wrap_limit = 90
        dummy_settings = Settings()
        dummy_settings.dm_cache_root = Path(dummy_cache_root)
        dummy_settings.dm_cache_variables = Path(dummy_cache_variables)
        dummy_settings.indent = dummy_indent
        dummy_settings.text_wrap_limit = dummy_text_wrap_limit

        # Current working directory related mocked items.
        dummy_cwd = "my_cwd"
        mocker.patch("dotmodules.modules.hooks.os.getcwd", return_value=dummy_cwd)

        # Hook's link list dummy values.
        dummy_link_path_to_target_1 = "my_link_path_to_target_1"
        dummy_link_path_to_symlink_1 = "my_link_path_to_symlink_1"
        dummy_link_name_1 = "my_link_name_1"

        dummy_link_path_to_target_2 = "my_link_path_to_target_2"
        dummy_link_path_to_symlink_2 = "my_link_path_to_symlink_2"
        dummy_link_name_2 = "my_link_name_2"

        dummy_links = [
            LinkItem(
                path_to_target=dummy_link_path_to_target_1,
                path_to_symlink=dummy_link_path_to_symlink_1,
                name=dummy_link_name_1,
            ),
            LinkItem(
                path_to_target=dummy_link_path_to_target_2,
                path_to_symlink=dummy_link_path_to_symlink_2,
                name=dummy_link_name_2,
            ),
        ]

        # Path manager related mocked items and dummy values.
        mock_path_manager = mocker.patch("dotmodules.modules.hooks.PathManager")
        # Two calls mocking for the links local path to target resolving.
        dummy_resolved_link_path_to_target_1 = "my_resolved_link_path_to_target_1"
        dummy_resolved_link_path_to_target_2 = "my_resolved_link_path_to_target_2"
        mock_path_manager.return_value.resolve_local_path.side_effect = [
            dummy_resolved_link_path_to_target_1,
            dummy_resolved_link_path_to_target_2,
        ]
        # Three calls mocking for the hook adapter script absolute path resolving
        # and for the link absolute symlink path resolving.
        dummy_resolved_hook_adapter_script = "my_resolved_hook_adapter_script"
        dummy_resolved_link_path_to_symlink_1 = "my_resolved_link_path_to_symlink_1"
        dummy_resolved_link_path_to_symlink_2 = "my_resolved_link_path_to_symlink_2"
        mock_path_manager.return_value.resolve_absolute_path.side_effect = [
            dummy_resolved_hook_adapter_script,
            dummy_resolved_link_path_to_symlink_1,
            dummy_resolved_link_path_to_symlink_2,
        ]
        # Single relative path calculation for the relative dm repo root.
        dummy_relative_dm_repo_root = "my_relative_dm_repo_root"
        mock_path_manager.return_value.get_relative_path.return_value = (
            dummy_relative_dm_repo_root
        )

        # Shell adapter related dummy values and mocked items.
        dummy_status_code = 0
        mock_shell_adapter = mocker.patch("dotmodules.modules.hooks.ShellAdapter")
        mock_shell_adapter.return_value.execute_interactively.return_value = (
            dummy_status_code
        )

        # Assembly of the expected command as a list of string. This will be passed
        # to the shell adapter.
        expected_command = [
            # 0 - hook adapter script absolute path
            dummy_resolved_hook_adapter_script,
            # 1 - DM_REPO_ROOT
            dummy_relative_dm_repo_root,
            # 2 - dm__config__target_hook_name
            LinkDeploymentHook.NAME,  # The link deployment hook has a fixed name.
            # 3 - dm__config__target_hook_priority
            str(0),  # The link deployment hook has fixed priority 0.
            # 4 - dm__config__target_module_name
            dummy_module_name,
            # 5 - dm__config__dm_cache_root
            dummy_cache_root,
            # 6 - dm__config__dm_cache_variables
            dummy_cache_variables,
            # 7 - dm__config__indent
            str(dummy_indent),
            # 8 - dm__config__wrap_limit
            str(dummy_text_wrap_limit),
            # 9 - link_path_to_target_1
            dummy_resolved_link_path_to_target_1,
            # 10 - link_path_to_symlink_1
            dummy_resolved_link_path_to_symlink_1,
            # 11 - link_path_to_target_2
            dummy_resolved_link_path_to_target_2,
            # 12 - link_path_to_symlink_2
            dummy_resolved_link_path_to_symlink_2,
        ]

        # =========================================================================
        #  EXECUTION
        # =========================================================================

        hook = LinkDeploymentHook(links=dummy_links)

        # To be able to execute the hook, its exeecution context needs to be
        # initialized from the corrrsponding module and from the settings
        # objects.
        hook.initialize_execution_context(module=dummy_module, settings=dummy_settings)
        result = hook.execute()

        # =========================================================================
        #  ASSERTION
        # =========================================================================

        assert result.status_code == dummy_status_code
        assert not result.execution_result

        # Shell adapter mocked call checking.
        mock_shell_adapter.return_value.execute_interactively.assert_called_with(
            command=expected_command, cwd=dummy_module_root
        )

        # Path manager mocked call checking.
        mock_path_manager.return_value.resolve_local_path.assert_has_calls(
            [
                mocker.call(dummy_link_path_to_target_1),
                mocker.call(dummy_link_path_to_target_2),
            ]
        )
        mock_path_manager.return_value.resolve_absolute_path.assert_has_calls(
            [
                mocker.call(HookAdapterScript.LINK_DEPLOYMENT, resolve_symlinks=True),
                mocker.call(dummy_link_path_to_symlink_1),
                mocker.call(dummy_link_path_to_symlink_2),
            ]
        )
        mock_path_manager.return_value.get_relative_path.assert_called_with(
            from_path=dummy_module_root, to_path=dummy_cwd
        )

    def test__link_cleanup_hook_can_build_its_arguments(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        # =========================================================================
        #  SETUP
        # =========================================================================

        # Module related dummy values.
        dummy_module_root = tmp_path
        dummy_module_name = "my_module_name"
        dummy_module = mocker.MagicMock()
        dummy_module.name = dummy_module_name
        dummy_module.root = dummy_module_root

        # Settings related dummy values and mocked items.
        dummy_cache_root = "my_cache_root"
        dummy_cache_variables = "my_cache_variables"
        dummy_indent = "my_indent"
        dummy_text_wrap_limit = 90
        dummy_settings = Settings()
        dummy_settings.dm_cache_root = Path(dummy_cache_root)
        dummy_settings.dm_cache_variables = Path(dummy_cache_variables)
        dummy_settings.indent = dummy_indent
        dummy_settings.text_wrap_limit = dummy_text_wrap_limit

        # Current working directory related mocked items.
        dummy_cwd = "my_cwd"
        mocker.patch("dotmodules.modules.hooks.os.getcwd", return_value=dummy_cwd)

        # Hook's link list dummy values.
        dummy_link_path_to_target_1 = "my_link_path_to_target_1"
        dummy_link_path_to_symlink_1 = "my_link_path_to_symlink_1"
        dummy_link_name_1 = "my_link_name_1"

        dummy_link_path_to_target_2 = "my_link_path_to_target_2"
        dummy_link_path_to_symlink_2 = "my_link_path_to_symlink_2"
        dummy_link_name_2 = "my_link_name_2"

        dummy_links = [
            LinkItem(
                path_to_target=dummy_link_path_to_target_1,
                path_to_symlink=dummy_link_path_to_symlink_1,
                name=dummy_link_name_1,
            ),
            LinkItem(
                path_to_target=dummy_link_path_to_target_2,
                path_to_symlink=dummy_link_path_to_symlink_2,
                name=dummy_link_name_2,
            ),
        ]

        # Path manager related mocked items and dummy values.
        mock_path_manager = mocker.patch("dotmodules.modules.hooks.PathManager")
        # Three calls mocking for the hook adapter script absolute path resolving
        # and for the link absolute symlink path resolving.
        dummy_resolved_hook_adapter_script = "my_resolved_hook_adapter_script"
        dummy_resolved_link_path_to_symlink_1 = "my_resolved_link_path_to_symlink_1"
        dummy_resolved_link_path_to_symlink_2 = "my_resolved_link_path_to_symlink_2"
        mock_path_manager.return_value.resolve_absolute_path.side_effect = [
            dummy_resolved_hook_adapter_script,
            dummy_resolved_link_path_to_symlink_1,
            dummy_resolved_link_path_to_symlink_2,
        ]
        # Single relative path calculation for the relative dm repo root.
        dummy_relative_dm_repo_root = "my_relative_dm_repo_root"
        mock_path_manager.return_value.get_relative_path.return_value = (
            dummy_relative_dm_repo_root
        )

        # Shell adapter related dummy values and mocked items.
        dummy_status_code = 0
        mock_shell_adapter = mocker.patch("dotmodules.modules.hooks.ShellAdapter")
        mock_shell_adapter.return_value.execute_interactively.return_value = (
            dummy_status_code
        )

        # Assembly of the expected command as a list of string. This will be passed
        # to the shell adapter.
        expected_command = [
            # 0 - hook adapter script absolute path
            dummy_resolved_hook_adapter_script,
            # 1 - DM_REPO_ROOT
            dummy_relative_dm_repo_root,
            # 2 - dm__config__target_hook_name
            LinkCleanUpHook.NAME,  # The link deployment hook has a fixed name.
            # 3 - dm__config__target_hook_priority
            str(0),  # The link deployment hook has fixed priority 0.
            # 4 - dm__config__target_module_name
            dummy_module_name,
            # 5 - dm__config__dm_cache_root
            dummy_cache_root,
            # 6 - dm__config__dm_cache_variables
            dummy_cache_variables,
            # 7 - dm__config__indent
            str(dummy_indent),
            # 8 - dm__config__wrap_limit
            str(dummy_text_wrap_limit),
            # 9 - link_path_to_symlink_1
            dummy_resolved_link_path_to_symlink_1,
            # 10 - link_path_to_symlink_2
            dummy_resolved_link_path_to_symlink_2,
        ]

        # =========================================================================
        #  EXECUTION
        # =========================================================================

        hook = LinkCleanUpHook(links=dummy_links)

        # To be able to execute the hook, its exeecution context needs to be
        # initialized from the corrrsponding module and from the settings
        # objects.
        hook.initialize_execution_context(module=dummy_module, settings=dummy_settings)
        result = hook.execute()

        # =========================================================================
        #  ASSERTION
        # =========================================================================

        assert result.status_code == dummy_status_code
        assert not result.execution_result

        # Shell adapter mocked call checking.
        mock_shell_adapter.return_value.execute_interactively.assert_called_with(
            command=expected_command, cwd=dummy_module_root
        )

        # Path manager mocked call checking.
        mock_path_manager.return_value.resolve_local_path.assert_not_called()
        mock_path_manager.return_value.resolve_absolute_path.assert_has_calls(
            [
                mocker.call(HookAdapterScript.LINK_CLEAN_UP, resolve_symlinks=True),
                mocker.call(dummy_link_path_to_symlink_1),
                mocker.call(dummy_link_path_to_symlink_2),
            ]
        )
        mock_path_manager.return_value.get_relative_path.assert_called_with(
            from_path=dummy_module_root, to_path=dummy_cwd
        )


class TestHookDescriptionGatheringCases:
    def test__shell_script_hook_can_describe_itself(self) -> None:
        dummy_path_to_script = "./dummy.script"
        dummy_hook_name = "my_hook_name"
        dummy_hook_priority = 42

        hook = ShellScriptHook(
            path_to_script=dummy_path_to_script,
            name=dummy_hook_name,
            priority=dummy_hook_priority,
        )

        expected_description = (
            f"Runs local script <<UNDERLINE>>{dummy_path_to_script}<<RESET>>"
        )
        assert hook.hook_description == expected_description

    def test__variable_status_hook_can_describe_itself(self) -> None:
        dummy_path_to_script = "./dummy.script"
        dummy_variable_name = "MY_VAR"

        hook = VariableStatusHook(
            path_to_script=dummy_path_to_script,
            variable_name=dummy_variable_name,
        )

        expected_description = (
            f"Retrieves deployment statistics for variable '{dummy_variable_name}' "
            f"through script <<UNDERLINE>>{dummy_path_to_script}<<RESET>>"
        )
        assert hook.hook_description == expected_description

    def test__link_deployment_hook_can_describe_itself__case_1(self) -> None:
        dummy_links = [
            LinkItem(
                path_to_target="irrelevant",
                path_to_symlink="irrelevant",
                name="irrelevant",
            ),
        ]

        hook = LinkDeploymentHook(links=dummy_links)

        expected_description = "Deploys 1 link"
        assert hook.hook_description == expected_description

    def test__link_deployment_hook_can_describe_itself__case_2(self) -> None:
        dummy_links = [
            LinkItem(
                path_to_target="irrelevant",
                path_to_symlink="irrelevant",
                name="irrelevant",
            ),
            LinkItem(
                path_to_target="irrelevant",
                path_to_symlink="irrelevant",
                name="irrelevant",
            ),
        ]

        hook = LinkDeploymentHook(links=dummy_links)

        expected_description = "Deploys 2 links"
        assert hook.hook_description == expected_description

    def test__link_cleanup_hook_can_describe_itself__case_1(self) -> None:
        dummy_links = [
            LinkItem(
                path_to_target="irrelevant",
                path_to_symlink="irrelevant",
                name="irrelevant",
            ),
        ]

        hook = LinkCleanUpHook(links=dummy_links)

        expected_description = "Cleans up 1 link"
        assert hook.hook_description == expected_description

    def test__link_cleanup_hook_can_describe_itself__case_2(self) -> None:
        dummy_links = [
            LinkItem(
                path_to_target="irrelevant",
                path_to_symlink="irrelevant",
                name="irrelevant",
            ),
            LinkItem(
                path_to_target="irrelevant",
                path_to_symlink="irrelevant",
                name="irrelevant",
            ),
        ]

        hook = LinkCleanUpHook(links=dummy_links)

        expected_description = "Cleans up 2 links"
        assert hook.hook_description == expected_description


class TestHookErrorReportingCases:
    def test__shell_script_hook__valid_path_to_script__no_errors(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        dummy_path_to_script = "./dummy.script"
        dummy_hook_name = "my_hook_name"
        dummy_hook_priority = 42

        dummy_script = tmp_path / dummy_path_to_script
        dummy_script.touch()

        hook = ShellScriptHook(
            path_to_script=dummy_path_to_script,
            name=dummy_hook_name,
            priority=dummy_hook_priority,
        )

        mock_path_manager = mocker.MagicMock()
        mock_path_manager.resolve_local_path.return_value = dummy_script

        assert hook.report_errors(path_manager=mock_path_manager) == []

        mock_path_manager.resolve_local_path.assert_called_with(dummy_path_to_script)

    def test__shell_script_hook__file_not_exists__error_should_be_reported(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        dummy_path_to_script = "./dummy.script"
        dummy_hook_name = "my_hook_name"
        dummy_hook_priority = 42

        dummy_script = tmp_path / dummy_path_to_script
        # NOTE: the file path won't be touched.

        hook = ShellScriptHook(
            path_to_script=dummy_path_to_script,
            name=dummy_hook_name,
            priority=dummy_hook_priority,
        )

        mock_path_manager = mocker.MagicMock()
        mock_path_manager.resolve_local_path.return_value = dummy_script

        expected_errors = [
            f"ShellScriptHook[{dummy_hook_name}]: path_to_script '{dummy_path_to_script}' does not name a file!",
        ]
        assert hook.report_errors(path_manager=mock_path_manager) == expected_errors

        mock_path_manager.resolve_local_path.assert_called_with(dummy_path_to_script)

    def test__variable_status_hook__valid_path_to_script__no_errors(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        dummy_path_to_script = "./dummy.script"
        dummy_variable_name = "MY_VAR"

        dummy_script = tmp_path / dummy_path_to_script
        dummy_script.touch()

        hook = VariableStatusHook(
            path_to_script=dummy_path_to_script,
            variable_name=dummy_variable_name,
        )

        mock_path_manager = mocker.MagicMock()
        mock_path_manager.resolve_local_path.return_value = dummy_script

        assert hook.report_errors(path_manager=mock_path_manager) == []

        mock_path_manager.resolve_local_path.assert_called_with(dummy_path_to_script)

    def test__variable_status_hook__file_not_exists__error_should_be_reported(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        dummy_path_to_script = "./dummy.script"
        dummy_variable_name = "MY_VAR"

        dummy_script = tmp_path / dummy_path_to_script
        # NOTE: the file path won't be touched.

        hook = VariableStatusHook(
            path_to_script=dummy_path_to_script,
            variable_name=dummy_variable_name,
        )

        mock_path_manager = mocker.MagicMock()
        mock_path_manager.resolve_local_path.return_value = dummy_script

        expected_errors = [
            f"VariableStatusHook[{dummy_variable_name}]: path_to_script '{dummy_path_to_script}' does not name a file!"
        ]
        assert hook.report_errors(path_manager=mock_path_manager) == expected_errors

        mock_path_manager.resolve_local_path.assert_called_with(dummy_path_to_script)


class TestLinkDeploymentHookErrorReportingCases:
    def test__link_deployment_hook__no_errors_should_be_reported(
        self, mocker: MockerFixture
    ) -> None:
        dummy_links = [
            LinkItem(
                path_to_target="irrelevant",
                path_to_symlink="irrelevant",
                name="irrelevant",
            ),
        ]

        mock_path_manager = mocker.MagicMock()

        hook = LinkDeploymentHook(links=dummy_links)

        # The link deployment hook should not report any errors.
        assert hook.report_errors(path_manager=mock_path_manager) == []


class TestLinkCleanupHookErrorReportingCases:
    def test__link_cleanup_hook__no_errors_should_be_reported(
        self, mocker: MockerFixture
    ) -> None:
        dummy_links = [
            LinkItem(
                path_to_target="irrelevant",
                path_to_symlink="irrelevant",
                name="irrelevant",
            ),
        ]

        mock_path_manager = mocker.MagicMock()

        hook = LinkCleanUpHook(links=dummy_links)

        # The link cleanup hook should not report any errors.
        assert hook.report_errors(path_manager=mock_path_manager) == []


class TestVariableStatusHookErrorReportingCases:
    def test__variable_status_hook__valid_path_to_script__no_errors(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        dummy_path_to_script = "./dummy.script"
        dummy_variable_name = "my_hook_name"

        dummy_script = tmp_path / dummy_path_to_script
        dummy_script.touch()

        hook = VariableStatusHook(
            path_to_script=dummy_path_to_script,
            variable_name=dummy_variable_name,
        )

        mock_path_manager = mocker.MagicMock()
        mock_path_manager.resolve_local_path.return_value = dummy_script

        assert hook.report_errors(path_manager=mock_path_manager) == []

        mock_path_manager.resolve_local_path.assert_called_with(dummy_path_to_script)

    def test__variable_stastus_hook__file_not_ecists__error_should_be_reported(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        dummy_path_to_script = "./dummy.script"
        dummy_variable_name = "my_hook_name"

        dummy_script = tmp_path / dummy_path_to_script
        # NOTE: the file path won't be touched.

        hook = VariableStatusHook(
            path_to_script=dummy_path_to_script,
            variable_name=dummy_variable_name,
        )

        mock_path_manager = mocker.MagicMock()
        mock_path_manager.resolve_local_path.return_value = dummy_script

        expected_errors = [
            f"VariableStatusHook[{dummy_variable_name}]: path_to_script '{dummy_path_to_script}' does not name a file!",
        ]
        assert hook.report_errors(path_manager=mock_path_manager) == expected_errors

        mock_path_manager.resolve_local_path.assert_called_with(dummy_path_to_script)
