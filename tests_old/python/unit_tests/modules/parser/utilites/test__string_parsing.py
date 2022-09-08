from unittest.mock import MagicMock

import pytest

from dotmodules.modules.loader import LoaderError
from dotmodules.modules.parser import ConfigParser, ParserError


class TestStringParsing:
    def test__valid_string_can_be_parsed(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "key"
        dummy_value = "some value"
        mock_loader.get.return_value = dummy_value

        result = parser._parse_string(key=dummy_key)
        assert result == dummy_value

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__missing_key__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "invalid_key"
        mock_loader.get.side_effect = LoaderError("missing key")

        with pytest.raises(ParserError) as exception_info:
            parser._parse_string(key=dummy_key)

        expected = f"Mandatory '{dummy_key}' section is missing!"
        assert exception_info.match(expected)

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__missing_key__but_not_mandatory__empty_should_be_returned(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "invalid_key"
        mock_loader.get.side_effect = LoaderError("missing key")

        result = parser._parse_string(key=dummy_key, mandatory=False)

        assert result == ""

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__empty_value__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_value = ""
        dummy_key = "key"
        mock_loader.get.return_value = dummy_value

        with pytest.raises(ParserError) as exception_info:
            parser._parse_string(key=dummy_key)

        expected = f"Empty value for section '{dummy_key}'!"
        assert exception_info.match(expected)

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__empty_value__but_not_mandatory__empty_should_be_returned(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_value = ""
        dummy_key = "invalid_key"
        mock_loader.get.return_value = dummy_value

        result = parser._parse_string(key=dummy_key, mandatory=False)

        assert result == ""

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__non_string_value__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_value = ["this", "is", "not", "a", "string"]
        dummy_key = "key"
        mock_loader.get.return_value = dummy_value

        with pytest.raises(ParserError) as exception_info:
            parser._parse_string(key=dummy_key)

        expected = f"Value for section '{dummy_key}' should be a string, got list!"
        assert exception_info.match(expected)

        mock_loader.get.assert_called_with(key=dummy_key)
