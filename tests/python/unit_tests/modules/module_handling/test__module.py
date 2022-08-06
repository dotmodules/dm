from pathlib import Path
from typing import List, Union, cast

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.hooks import (
    LinkCleanUpHook,
    LinkDeploymentHook,
    ShellScriptHook,
)
from dotmodules.modules.links import LinkItem
from dotmodules.modules.modules import Module, ModuleStatus
from dotmodules.modules.parser import HookItemDict, LinkItemDict, ParserError


class TestModuleLoadingInternalCases:
    def test__links_can_be_created(self) -> None:
        link_items: List[LinkItemDict] = [
            {
                "path_to_target": "path_to_target_1",
                "path_to_symlink": "path_to_symlink_1",
                "name": "name_1",
            },
            {
                "path_to_target": "path_to_target_2",
                "path_to_symlink": "path_to_symlink_2",
                "name": "name_2",
            },
        ]

        links = Module._create_links(link_items=link_items)

        assert len(links) == 2

        link = links[0]
        assert link.path_to_target == "path_to_target_1"
        assert link.path_to_symlink == "path_to_symlink_1"
        assert link.name == "name_1"

        link = links[1]
        assert link.path_to_target == "path_to_target_2"
        assert link.path_to_symlink == "path_to_symlink_2"
        assert link.name == "name_2"

    def test__hooks_can_be_created(self) -> None:
        hook_items: List[HookItemDict] = [
            {
                "path_to_script": "path_to_script_1",
                "name": "name_1",
                "priority": 1,
            },
            {
                "path_to_script": "path_to_script_2",
                "name": "name_2",
                "priority": 2,
            },
        ]

        hooks = Module._create_hooks(hook_items=hook_items)

        assert len(hooks) == 2

        hook = cast(ShellScriptHook, hooks[0])
        assert hook.path_to_script == "path_to_script_1"
        assert hook.name == "name_1"
        assert hook.priority == 1

        hook = cast(ShellScriptHook, hooks[1])
        assert hook.path_to_script == "path_to_script_2"
        assert hook.name == "name_2"
        assert hook.priority == 2

    def test__hooks_can_be__validated__no_error(self) -> None:
        hooks: List[Union[ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]] = [
            ShellScriptHook(
                path_to_script="path_to_script_1",
                name="name_1",
                priority=1,
            ),
            ShellScriptHook(
                path_to_script="path_to_script_2",
                name="name_2",
                priority=1,
            ),
        ]
        Module._validate_hooks(hooks=hooks)

    @pytest.mark.parametrize(
        "reserved_name",
        [
            LinkDeploymentHook.NAME,
            LinkCleanUpHook.NAME,
        ],
    )
    def test__hooks_can_be__error__reserved_hook_name(self, reserved_name: str) -> None:
        hooks: List[Union[ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]] = [
            ShellScriptHook(
                path_to_script="path_to_script_1",
                name=reserved_name,
                priority=1,
            ),
            ShellScriptHook(
                path_to_script="path_to_script_2",
                name="name_2",
                priority=1,
            ),
        ]
        with pytest.raises(ParserError) as exception_info:
            Module._validate_hooks(hooks=hooks)

        expected = f"Cannot use reserved hook name '{reserved_name}' in section 'hooks' at index 1!"
        assert exception_info.match(expected)

    def test__default_link_hooks_can_be_created(self) -> None:
        links = [
            LinkItem(
                path_to_target="path_to_target_1",
                path_to_symlink="path_to_target_1",
                name="name_1",
            ),
            LinkItem(
                path_to_target="path_to_target_2",
                path_to_symlink="path_to_target_2",
                name="name_2",
            ),
        ]

        default_hooks = Module._create_default_link_hooks(links=links)

        assert len(default_hooks) == 2

        hook = default_hooks[0]
        assert isinstance(hook, LinkDeploymentHook)
        assert hook.links == links

        hook = default_hooks[1]
        assert isinstance(hook, LinkCleanUpHook)
        assert hook.links == links


class TestModuleErrorCollectingCases:
    def test__errors_can_be_collected_from_hooks_and_links(
        self, mocker: MockerFixture
    ) -> None:
        link = LinkItem(
            path_to_target="path_to_target_1",
            path_to_symlink="path_to_target_1",
            name="link_name_1",
        )
        hook = ShellScriptHook(
            path_to_script="path_to_script_1",
            name="hook_name_1",
            priority=1,
        )
        mock_link_report_errors = mocker.patch.object(
            link, "report_errors", return_value=["link_error_1", "link_error_2"]
        )
        mock_hook_report_errors = mocker.patch.object(
            hook, "report_errors", return_value=["hook_error_1", "hook_error_2"]
        )

        module = Module(
            root=Path("module/root"),
            name="module_name_1",
            version="module_version_1",
            enabled=True,
            documentation=["line_1"],
            variables={},
            links=[link],
            hooks=[hook],
        )

        errors = module.errors

        assert len(errors) == 4
        assert errors == [
            "link_error_1",
            "link_error_2",
            "hook_error_1",
            "hook_error_2",
        ]

        mock_link_report_errors.assert_called_once()
        mock_hook_report_errors.assert_called_once()


class TestModuleStatusCalculationCases:
    def test__errors_reported__status_will_be_error(
        self, mocker: MockerFixture
    ) -> None:
        module = Module(
            root=Path("module/root"),
            name="module_name_1",
            version="module_version_1",
            enabled=True,
            documentation=["line_1"],
            variables={},
            links=[],
            hooks=[],
        )
        mock_module_error = mocker.patch.object(
            Module, "errors", new_callable=mocker.PropertyMock
        )
        mock_module_error.return_value = ["error"]

        assert module.status == ModuleStatus.ERROR

        mock_module_error.assert_called_once()

    def test__module_disabled__status_will_be_disabled(self) -> None:
        module = Module(
            root=Path("module/root"),
            name="module_name_1",
            version="module_version_1",
            enabled=False,
            documentation=["line_1"],
            variables={},
            links=[],
            hooks=[],
        )
        assert module.status == ModuleStatus.DISABLED

    def test__disabled_status_has_priority_over_error(
        self, mocker: MockerFixture
    ) -> None:
        module = Module(
            root=Path("module/root"),
            name="module_name_1",
            version="module_version_1",
            enabled=False,
            documentation=["line_1"],
            variables={},
            links=[],
            hooks=[],
        )
        mock_module_error = mocker.patch.object(
            Module, "errors", new_callable=mocker.PropertyMock
        )
        mock_module_error.return_value = ["error"]

        assert module.status == ModuleStatus.DISABLED

        mock_module_error.assert_not_called()

    def test__no_errors__every_deployment_status_reported__status_will_be_deployed(
        self, mocker: MockerFixture
    ) -> None:
        link = LinkItem(
            path_to_target="path_to_target_1",
            path_to_symlink="path_to_target_1",
            name="link_name_1",
        )
        module = Module(
            root=Path("module/root"),
            name="module_name_1",
            version="module_version_1",
            enabled=True,
            documentation=["line_1"],
            variables={},
            links=[link],
            hooks=[],
        )

        mock_module_error = mocker.patch.object(
            Module, "errors", new_callable=mocker.PropertyMock
        )
        mock_module_error.return_value = []

        mock_link_existence_check = mocker.patch.object(
            link, "check_if_link_exists", return_value=True
        )
        mock_target_matched_check = mocker.patch.object(
            link, "check_if_target_matched", return_value=True
        )

        assert module.status == ModuleStatus.DEPLOYED

        mock_module_error.assert_called_once()
        mock_link_existence_check.assert_called_once()
        mock_target_matched_check.assert_called_once()

    def test__no_error__not_all_deployment_status__status_will_be_pending(
        self, mocker: MockerFixture
    ) -> None:
        link = LinkItem(
            path_to_target="path_to_target_1",
            path_to_symlink="path_to_target_1",
            name="link_name_1",
        )
        module = Module(
            root=Path("module/root"),
            name="module_name_1",
            version="module_version_1",
            enabled=True,
            documentation=["line_1"],
            variables={},
            links=[link],
            hooks=[],
        )

        mock_module_error = mocker.patch.object(
            Module, "errors", new_callable=mocker.PropertyMock
        )
        mock_module_error.return_value = []

        mock_link_existence_check = mocker.patch.object(
            link, "check_if_link_exists", return_value=False
        )
        mock_target_matched_check = mocker.patch.object(
            link, "check_if_target_matched", return_value=True
        )

        assert module.status == ModuleStatus.PENDING

        mock_module_error.assert_called_once()
        mock_link_existence_check.assert_called_once()
        mock_target_matched_check.assert_not_called()  # Due to lazy evaluation..
