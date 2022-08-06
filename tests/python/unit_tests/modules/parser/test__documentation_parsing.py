from pytest_mock.plugin import MockerFixture

from dotmodules.modules.parser import ConfigParser


class TestDocumentationParsing:
    def test__documentation_can_be_parsed__without_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        mock_parse_string = mocker.patch.object(parser, "_parse_string")
        mock_parse_string.return_value = "line1\nline2"

        result = parser.parse_documentation(deployment_target="")
        assert result == [
            "line1",
            "line2",
        ]

        mock_parse_string.assert_called_once_with(key="documentation", mandatory=False)

    def test__documentation_can_be_parsed__with_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        mock_parse_string = mocker.patch.object(parser, "_parse_string")
        mock_parse_string.side_effect = [
            "line1\nline2",
            "line3\nline4",
        ]

        result = parser.parse_documentation(deployment_target=dummy_deployment_target)
        assert result == [
            "line1",
            "line2",
            "",
            "line3",
            "line4",
        ]

        mock_parse_string.assert_has_calls(
            [
                mocker.call(key="documentation", mandatory=False),
                mocker.call(
                    key=f"documentation__{dummy_deployment_target}", mandatory=False
                ),
            ]
        )

    def test__documentation_can_be_parsed__missing_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        mock_parse_string = mocker.patch.object(parser, "_parse_string")
        mock_parse_string.side_effect = [
            "line1\nline2",
            "",  # A missing deployment target would return an empty string.
        ]

        result = parser.parse_documentation(deployment_target=dummy_deployment_target)
        assert result == [
            "line1",
            "line2",
        ]

        mock_parse_string.assert_has_calls(
            [
                mocker.call(key="documentation", mandatory=False),
                mocker.call(
                    key=f"documentation__{dummy_deployment_target}", mandatory=False
                ),
            ]
        )

    def test__documentation_can_be_parsed__only_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"
        mock_parse_string = mocker.patch.object(parser, "_parse_string")
        mock_parse_string.side_effect = [
            "",  # A missing main documentation would return an empty string.
            "line3\nline4",
        ]

        result = parser.parse_documentation(deployment_target=dummy_deployment_target)
        # Theree should be no an empty line prefix.
        assert result == [
            "line3",
            "line4",
        ]

        mock_parse_string.assert_has_calls(
            [
                mocker.call(key="documentation", mandatory=False),
                mocker.call(
                    key=f"documentation__{dummy_deployment_target}", mandatory=False
                ),
            ]
        )
