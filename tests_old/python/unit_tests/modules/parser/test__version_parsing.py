from pytest_mock.plugin import MockerFixture

from dotmodules.modules.parser import ConfigParser


class TestVersionParsing:
    def test__version_can_be_parsed(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_version = "my_version"
        mock_parse_string = mocker.patch.object(parser, "_parse_string")
        mock_parse_string.return_value = dummy_version

        result = parser.parse_version()
        assert result == dummy_version

        mock_parse_string.assert_called_with(key="version")
