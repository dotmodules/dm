from pytest_mock.plugin import MockerFixture

from dotmodules.modules.parser import ConfigParser


class TestNameParsing:
    def test__name_can_be_parsed(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_name = "my_name"
        mock_parse_string = mocker.patch.object(parser, "_parse_string")
        mock_parse_string.return_value = dummy_name

        result = parser.parse_name()
        assert result == dummy_name

        mock_parse_string.assert_called_with(key="name")
