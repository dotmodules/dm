from typing import List

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.parser import ConfigParser, LinkItemDict, ParserError


class TestLinkParsing:
    def test__missing_global_links__without_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_global_links: List[LinkItemDict] = []
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.return_value = dummy_global_links

        expected_links = dummy_global_links

        result = parser.parse_links(deployment_target="")
        assert result == expected_links

        mock_parse_item_list.assert_called_once_with(
            key="links",
            expected_item={
                "path_to_target": "string",
                "path_to_symlink": "string",
                "name": "string",
            },
        )

    def test__missing_global_links__with_missing_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_links: List[LinkItemDict] = []
        dummy_deployment_target_links: List[LinkItemDict] = []
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_links,
            dummy_deployment_target_links,
        ]

        expected_links = dummy_global_links

        result = parser.parse_links(deployment_target=dummy_deployment_target)
        assert result == expected_links

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="links",
                    expected_item={
                        "path_to_target": "string",
                        "path_to_symlink": "string",
                        "name": "string",
                    },
                ),
                mocker.call(
                    key=f"links__{dummy_deployment_target}",
                    expected_item={
                        "path_to_target": "string",
                        "path_to_symlink": "string",
                        "name": "string",
                    },
                ),
            ]
        )

    def test__missing_global_links__with_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_links: List[LinkItemDict] = []
        dummy_deployment_target_links: List[LinkItemDict] = [
            {
                "path_to_target": "my_path_to_target_3",
                "path_to_symlink": "my_path_to_symlink_3",
                "name": "my_name_3",
            },
            {
                "path_to_target": "my_path_to_target_4",
                "path_to_symlink": "my_path_to_symlink_4",
                "name": "my_name_4",
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_links,
            dummy_deployment_target_links,
        ]

        expected_links = dummy_global_links + dummy_deployment_target_links

        result = parser.parse_links(deployment_target=dummy_deployment_target)
        assert result == expected_links

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="links",
                    expected_item={
                        "path_to_target": "string",
                        "path_to_symlink": "string",
                        "name": "string",
                    },
                ),
                mocker.call(
                    key=f"links__{dummy_deployment_target}",
                    expected_item={
                        "path_to_target": "string",
                        "path_to_symlink": "string",
                        "name": "string",
                    },
                ),
            ]
        )

    def test__global_links__without_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_global_links = [
            {
                "path_to_target": "my_path_to_target_1",
                "path_to_symlink": "my_path_to_symlink_1",
                "name": "my_name_1",
            },
            {
                "path_to_target": "my_path_to_target_2",
                "path_to_symlink": "my_path_to_symlink_2",
                "name": "my_name_2",
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.return_value = dummy_global_links

        expected_links = dummy_global_links

        result = parser.parse_links(deployment_target="")
        assert result == expected_links

        mock_parse_item_list.assert_called_once_with(
            key="links",
            expected_item={
                "path_to_target": "string",
                "path_to_symlink": "string",
                "name": "string",
            },
        )

    def test__global_links__with_missing_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_links = [
            {
                "path_to_target": "my_path_to_target_1",
                "path_to_symlink": "my_path_to_symlink_1",
                "name": "my_name_1",
            },
            {
                "path_to_target": "my_path_to_target_2",
                "path_to_symlink": "my_path_to_symlink_2",
                "name": "my_name_2",
            },
        ]
        dummy_deployment_target_links: List[LinkItemDict] = []
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_links,
            dummy_deployment_target_links,
        ]

        expected_links = dummy_global_links

        result = parser.parse_links(deployment_target=dummy_deployment_target)
        assert result == expected_links

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="links",
                    expected_item={
                        "path_to_target": "string",
                        "path_to_symlink": "string",
                        "name": "string",
                    },
                ),
                mocker.call(
                    key=f"links__{dummy_deployment_target}",
                    expected_item={
                        "path_to_target": "string",
                        "path_to_symlink": "string",
                        "name": "string",
                    },
                ),
            ]
        )

    def test__global_links__with_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_links = [
            {
                "path_to_target": "my_path_to_target_1",
                "path_to_symlink": "my_path_to_symlink_1",
                "name": "my_name_1",
            },
            {
                "path_to_target": "my_path_to_target_2",
                "path_to_symlink": "my_path_to_symlink_2",
                "name": "my_name_2",
            },
        ]
        dummy_deployment_target_links: List[LinkItemDict] = [
            {
                "path_to_target": "my_path_to_target_3",
                "path_to_symlink": "my_path_to_symlink_3",
                "name": "my_name_3",
            },
            {
                "path_to_target": "my_path_to_target_4",
                "path_to_symlink": "my_path_to_symlink_4",
                "name": "my_name_4",
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_links,
            dummy_deployment_target_links,
        ]

        expected_links = dummy_global_links

        result = parser.parse_links(deployment_target=dummy_deployment_target)
        assert result == expected_links

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="links",
                    expected_item={
                        "path_to_target": "string",
                        "path_to_symlink": "string",
                        "name": "string",
                    },
                ),
                mocker.call(
                    key=f"links__{dummy_deployment_target}",
                    expected_item={
                        "path_to_target": "string",
                        "path_to_symlink": "string",
                        "name": "string",
                    },
                ),
            ]
        )

    def test__deployment_target_redefines_link__error_should_be_raised(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        dummy_global_links = [
            {
                "path_to_target": "my_path_to_target",
                "path_to_symlink": "my_path_to_symlink",
                "name": "my_name",
            },
        ]
        dummy_deployment_target_links = [
            {
                "path_to_target": "my_path_to_target",
                "path_to_symlink": "my_path_to_symlink",
                "name": "my_name",
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.side_effect = [
            dummy_global_links,
            dummy_deployment_target_links,
        ]

        with pytest.raises(ParserError) as error_context:
            parser.parse_links(deployment_target=dummy_deployment_target)

        expected_error_message = (
            "Deployment target specific link section "
            f"'links__{dummy_deployment_target}' contains an already "
            "defined link item!"
        )
        assert error_context.match(expected_error_message)

        mock_parse_item_list.assert_has_calls(
            [
                mocker.call(
                    key="links",
                    expected_item={
                        "path_to_target": "string",
                        "path_to_symlink": "string",
                        "name": "string",
                    },
                ),
                mocker.call(
                    key=f"links__{dummy_deployment_target}",
                    expected_item={
                        "path_to_target": "string",
                        "path_to_symlink": "string",
                        "name": "string",
                    },
                ),
            ]
        )
