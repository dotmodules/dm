from typing import List

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.parser import ConfigParser, HookItemDict, ParserError


class TestHookParsing:
    def test__missing_global_hooks__without_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_global_hooks: List[HookItemDict] = []
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.return_value = dummy_global_hooks

        expected_hooks = dummy_global_hooks

        result = parser.parse_hooks(deployment_target="")
        assert result == expected_hooks

        mock_parse_item_list.assert_called_once_with(
            key="hooks",
            expected_item={
                "path_to_script": "string",
                "name": "string",
                "priority": 0,
            },
        )

    def test__missing_global_hooks__with_missing_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_hooks: List[HookItemDict] = []
        dummy_deployment_target_hooks: List[HookItemDict] = []
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_hooks,
            dummy_deployment_target_hooks,
        ]

        expected_hooks = dummy_global_hooks

        result = parser.parse_hooks(deployment_target=dummy_deployment_target)
        assert result == expected_hooks

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="hooks",
                    expected_item={
                        "path_to_script": "string",
                        "name": "string",
                        "priority": 0,
                    },
                ),
                mocker.call(
                    key=f"hooks__{dummy_deployment_target}",
                    expected_item={
                        "path_to_script": "string",
                        "name": "string",
                        "priority": 0,
                    },
                ),
            ]
        )

    def test__missing_global_hooks__with_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_hooks: List[HookItemDict] = []
        dummy_deployment_target_hooks: List[HookItemDict] = [
            {
                "path_to_script": "my_path_to_script_3",
                "priority": 3,
                "name": "my_name_3",
            },
            {
                "path_to_script": "my_path_to_script_4",
                "priority": 4,
                "name": "my_name_4",
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_hooks,
            dummy_deployment_target_hooks,
        ]

        expected_hooks = dummy_global_hooks + dummy_deployment_target_hooks

        result = parser.parse_hooks(deployment_target=dummy_deployment_target)
        assert result == expected_hooks

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="hooks",
                    expected_item={
                        "path_to_script": "string",
                        "name": "string",
                        "priority": 0,
                    },
                ),
                mocker.call(
                    key=f"hooks__{dummy_deployment_target}",
                    expected_item={
                        "path_to_script": "string",
                        "name": "string",
                        "priority": 0,
                    },
                ),
            ]
        )

    def test__global_hooks__without_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_global_hooks = [
            {
                "path_to_script": "my_path_to_script_1",
                "priority": 1,
                "name": "my_name_1",
            },
            {
                "path_to_script": "my_path_to_script_2",
                "priority": 2,
                "name": "my_name_2",
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.return_value = dummy_global_hooks

        expected_hooks = dummy_global_hooks

        result = parser.parse_hooks(deployment_target="")
        assert result == expected_hooks

        mock_parse_item_list.assert_called_once_with(
            key="hooks",
            expected_item={
                "path_to_script": "string",
                "name": "string",
                "priority": 0,
            },
        )

    def test__global_hooks__with_missing_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_hooks = [
            {
                "path_to_script": "my_path_to_script_1",
                "priority": 1,
                "name": "my_name_1",
            },
            {
                "path_to_script": "my_path_to_script_2",
                "priority": 2,
                "name": "my_name_2",
            },
        ]
        dummy_deployment_target_hooks: List[HookItemDict] = []
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_hooks,
            dummy_deployment_target_hooks,
        ]

        expected_hooks = dummy_global_hooks

        result = parser.parse_hooks(deployment_target=dummy_deployment_target)
        assert result == expected_hooks

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="hooks",
                    expected_item={
                        "path_to_script": "string",
                        "name": "string",
                        "priority": 0,
                    },
                ),
                mocker.call(
                    key=f"hooks__{dummy_deployment_target}",
                    expected_item={
                        "path_to_script": "string",
                        "name": "string",
                        "priority": 0,
                    },
                ),
            ]
        )

    def test__global_hooks__with_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_hooks: List[HookItemDict] = [
            {
                "path_to_script": "my_path_to_script_1",
                "priority": 1,
                "name": "my_name_1",
            },
            {
                "path_to_script": "my_path_to_script_2",
                "priority": 2,
                "name": "my_name_2",
            },
        ]
        dummy_deployment_target_hooks: List[HookItemDict] = [
            {
                "path_to_script": "my_path_to_script_3",
                "priority": 3,
                "name": "my_name_3",
            },
            {
                "path_to_script": "my_path_to_script_4",
                "priority": 4,
                "name": "my_name_4",
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_hooks,
            dummy_deployment_target_hooks,
        ]

        expected_hooks = dummy_global_hooks

        result = parser.parse_hooks(deployment_target=dummy_deployment_target)
        assert result == expected_hooks

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="hooks",
                    expected_item={
                        "path_to_script": "string",
                        "name": "string",
                        "priority": 0,
                    },
                ),
                mocker.call(
                    key=f"hooks__{dummy_deployment_target}",
                    expected_item={
                        "path_to_script": "string",
                        "name": "string",
                        "priority": 0,
                    },
                ),
            ]
        )

    def test__deployment_target_redefines_hook__error_should_be_raised(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_hooks = [
            {
                "path_to_script": "my_path_to_script",
                "priority": 0,
                "name": "my_name",
            },
        ]
        dummy_deployment_target_hooks = [
            {
                "path_to_script": "my_path_to_script",
                "priority": 0,
                "name": "my_name",
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_hooks,
            dummy_deployment_target_hooks,
        ]

        with pytest.raises(ParserError) as error_context:
            parser.parse_hooks(deployment_target=dummy_deployment_target)

        expected_error_message = (
            "Deployment target specific hook section "
            f"'hooks__{dummy_deployment_target}' contains an already "
            "defined hook item!"
        )
        assert error_context.match(expected_error_message)

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="hooks",
                    expected_item={
                        "path_to_script": "string",
                        "name": "string",
                        "priority": 0,
                    },
                ),
                mocker.call(
                    key=f"hooks__{dummy_deployment_target}",
                    expected_item={
                        "path_to_script": "string",
                        "name": "string",
                        "priority": 0,
                    },
                ),
            ]
        )
