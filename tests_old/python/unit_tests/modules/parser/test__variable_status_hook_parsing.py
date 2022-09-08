from typing import List

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.parser import (
    ConfigParser,
    ParserError,
    VariableStatusHookItemDict,
)


class TestVariableStatusHookParsing:
    def test__missing_global_variable_status_hooks__without_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_global_hooks: List[VariableStatusHookItemDict] = []
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.return_value = dummy_global_hooks

        expected_hooks = dummy_global_hooks

        result = parser.parse_variable_status_hooks(deployment_target="")
        assert result == expected_hooks

        mock_parse_item_list.assert_called_once_with(
            key="variable_status_hooks",
            expected_item={
                "path_to_script": "string",
                "variable_name": "string",
                "prepare_step_necessary": False,
            },
        )

    def test__missing_global_variable_status_hooks__with_missing_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_hooks: List[VariableStatusHookItemDict] = []
        dummy_deployment_target_hooks: List[VariableStatusHookItemDict] = []
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_hooks,
            dummy_deployment_target_hooks,
        ]

        expected_hooks = dummy_global_hooks

        result = parser.parse_variable_status_hooks(
            deployment_target=dummy_deployment_target
        )
        assert result == expected_hooks

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="variable_status_hooks",
                    expected_item={
                        "path_to_script": "string",
                        "variable_name": "string",
                        "prepare_step_necessary": False,
                    },
                ),
                mocker.call(
                    key=f"variable_status_hooks__{dummy_deployment_target}",
                    expected_item={
                        "path_to_script": "string",
                        "variable_name": "string",
                        "prepare_step_necessary": False,
                    },
                ),
            ]
        )

    def test__missing_global_variable_status_hooks__with_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_hooks: List[VariableStatusHookItemDict] = []
        dummy_deployment_target_hooks: List[VariableStatusHookItemDict] = [
            {
                "path_to_script": "my_path_to_script_3",
                "variable_name": "var_3",
                "prepare_step_necessary": False,
            },
            {
                "path_to_script": "my_path_to_script_4",
                "variable_name": "var_4",
                "prepare_step_necessary": False,
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_hooks,
            dummy_deployment_target_hooks,
        ]

        expected_hooks = dummy_global_hooks + dummy_deployment_target_hooks

        result = parser.parse_variable_status_hooks(
            deployment_target=dummy_deployment_target
        )
        assert result == expected_hooks

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="variable_status_hooks",
                    expected_item={
                        "path_to_script": "string",
                        "variable_name": "string",
                        "prepare_step_necessary": False,
                    },
                ),
                mocker.call(
                    key=f"variable_status_hooks__{dummy_deployment_target}",
                    expected_item={
                        "path_to_script": "string",
                        "variable_name": "string",
                        "prepare_step_necessary": False,
                    },
                ),
            ]
        )

    def test__global_variable_status_hooks__without_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_global_hooks = [
            {
                "path_to_script": "my_path_to_script_1",
                "variable_name": "var_1",
                "prepare_step_necessary": False,
            },
            {
                "path_to_script": "my_path_to_script_2",
                "variable_name": "var_2",
                "prepare_step_necessary": False,
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.return_value = dummy_global_hooks

        expected_hooks = dummy_global_hooks

        result = parser.parse_variable_status_hooks(deployment_target="")
        assert result == expected_hooks

        mock_parse_item_list.assert_called_once_with(
            key="variable_status_hooks",
            expected_item={
                "path_to_script": "string",
                "variable_name": "string",
                "prepare_step_necessary": False,
            },
        )

    def test__global_variable_status_hooks__with_missing_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_hooks = [
            {
                "path_to_script": "my_path_to_script_1",
                "variable_name": "var_1",
                "prepare_step_necessary": False,
            },
            {
                "path_to_script": "my_path_to_script_2",
                "variable_name": "var_2",
                "prepare_step_necessary": False,
            },
        ]
        dummy_deployment_target_hooks: List[VariableStatusHookItemDict] = []
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_hooks,
            dummy_deployment_target_hooks,
        ]

        expected_hooks = dummy_global_hooks

        result = parser.parse_variable_status_hooks(
            deployment_target=dummy_deployment_target
        )
        assert result == expected_hooks

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="variable_status_hooks",
                    expected_item={
                        "path_to_script": "string",
                        "variable_name": "string",
                        "prepare_step_necessary": False,
                    },
                ),
                mocker.call(
                    key=f"variable_status_hooks__{dummy_deployment_target}",
                    expected_item={
                        "path_to_script": "string",
                        "variable_name": "string",
                        "prepare_step_necessary": False,
                    },
                ),
            ]
        )

    def test__global_variable_status_hooks__with_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_hooks: List[VariableStatusHookItemDict] = [
            {
                "path_to_script": "my_path_to_script_1",
                "variable_name": "var_1",
                "prepare_step_necessary": False,
            },
            {
                "path_to_script": "my_path_to_script_2",
                "variable_name": "var_2",
                "prepare_step_necessary": False,
            },
        ]
        dummy_deployment_target_hooks: List[VariableStatusHookItemDict] = [
            {
                "path_to_script": "my_path_to_script_3",
                "variable_name": "var_3",
                "prepare_step_necessary": False,
            },
            {
                "path_to_script": "my_path_to_script_4",
                "variable_name": "var_4",
                "prepare_step_necessary": False,
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_hooks,
            dummy_deployment_target_hooks,
        ]

        expected_hooks = dummy_global_hooks

        result = parser.parse_variable_status_hooks(
            deployment_target=dummy_deployment_target
        )
        assert result == expected_hooks

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="variable_status_hooks",
                    expected_item={
                        "path_to_script": "string",
                        "variable_name": "string",
                        "prepare_step_necessary": False,
                    },
                ),
                mocker.call(
                    key=f"variable_status_hooks__{dummy_deployment_target}",
                    expected_item={
                        "path_to_script": "string",
                        "variable_name": "string",
                        "prepare_step_necessary": False,
                    },
                ),
            ]
        )

    def test__deployment_target_redefines_variable_status_hook__error_should_be_raised(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_hooks = [
            {
                "path_to_script": "my_path_to_script",
                "variable_name": "var",
                "prepare_step_necessary": False,
            },
        ]
        dummy_deployment_target_hooks = [
            {
                "path_to_script": "my_path_to_script",
                "variable_name": "var",
                "prepare_step_necessary": False,
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_hooks,
            dummy_deployment_target_hooks,
        ]

        with pytest.raises(ParserError) as error_context:
            parser.parse_variable_status_hooks(
                deployment_target=dummy_deployment_target
            )

        expected_error_message = (
            "Deployment target specific hook section "
            f"'variable_status_hooks__{dummy_deployment_target}' contains an already "
            "defined hook item!"
        )
        assert error_context.match(expected_error_message)

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="variable_status_hooks",
                    expected_item={
                        "path_to_script": "string",
                        "variable_name": "string",
                        "prepare_step_necessary": False,
                    },
                ),
                mocker.call(
                    key=f"variable_status_hooks__{dummy_deployment_target}",
                    expected_item={
                        "path_to_script": "string",
                        "variable_name": "string",
                        "prepare_step_necessary": False,
                    },
                ),
            ]
        )
