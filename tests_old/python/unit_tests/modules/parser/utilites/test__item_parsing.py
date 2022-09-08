from unittest.mock import MagicMock

import pytest

from dotmodules.modules.loader import LoaderError
from dotmodules.modules.parser import ConfigParser, ParserError


class TestItemListParsing:
    def test__missing_key_should_be_converted_to_an_empty_list(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {"irrelevant": "irrelevant"}
        mock_loader.get.side_effect = LoaderError("missing key")

        result = parser._parse_item_list(
            key=dummy_key,
            # We are testing here with a simplified expected item type, ignoring
            # the mypy warning.
            expected_item=dummy_expected_item,  # type: ignore
        )

        assert result == []

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__none_value_should_be_converted_to_an_empty_list(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {"irrelevant": "irrelevant"}
        mock_loader.get.return_value = None

        result = parser._parse_item_list(
            key=dummy_key,
            # We are testing here with a simplified expected item type, ignoring
            # the mypy warning.
            expected_item=dummy_expected_item,  # type: ignore
        )

        assert result == []

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__empty_value_should_be_converted_to_an_empty_list(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {"irrelevant": "irrelevant"}
        mock_loader.get.return_value = {}

        result = parser._parse_item_list(
            key=dummy_key,
            # We are testing here with a simplified expected item type, ignoring
            # the mypy warning.
            expected_item=dummy_expected_item,  # type: ignore
        )

        assert result == []

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__not_a_list__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {
            "field_1": "string",
            "field_2": 42,
        }
        mock_loader.get.return_value = "I am not a list"

        with pytest.raises(ParserError) as exception_info:
            parser._parse_item_list(
                key=dummy_key,
                # We are testing here with a simplified expected item type,
                # ignoring the mypy warning.
                expected_item=dummy_expected_item,  # type: ignore
            )

        expected = "Invalid value for 'my_key'! It should contain a list of objects!"
        assert exception_info.match(expected)

    def test__not_a_list_of_dictionaries__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {
            "field_1": "string",
            "field_2": 42,
        }
        mock_loader.get.return_value = [42, {"hello": "hello"}]

        with pytest.raises(ParserError) as exception_info:
            parser._parse_item_list(
                key=dummy_key,
                # We are testing here with a simplified expected item type,
                # ignoring the mypy warning.
                expected_item=dummy_expected_item,  # type: ignore
            )

        expected = "Invalid value for 'my_key'! It should contain a list of objects!"
        assert exception_info.match(expected)

    def test__valid_item_can_be_parsed(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {
            "field_1": "string",
            "field_2": 42,
        }
        mock_loader.get.return_value = [
            {
                "field_1": "value_1",
                "field_2": 42,
            },
        ]

        result = parser._parse_item_list(
            key=dummy_key,
            # We are testing here with a simplified expected item type, ignoring
            # the mypy warning.
            expected_item=dummy_expected_item,  # type: ignore
        )

        assert result == [
            {
                "field_1": "value_1",
                "field_2": 42,
            },
        ]

    def test__multiple_valid_items_can_be_parsed(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {
            "field_1": "string",
            "field_2": 42,
        }
        mock_loader.get.return_value = [
            {
                "field_1": "value_1",
                "field_2": 42,
            },
            {
                "field_1": "value_2",
                "field_2": 43,
            },
        ]

        result = parser._parse_item_list(
            key=dummy_key,
            # We are testing here with a simplified expected item type, ignoring
            # the mypy warning.
            expected_item=dummy_expected_item,  # type: ignore
        )

        assert result == [
            {
                "field_1": "value_1",
                "field_2": 42,
            },
            {
                "field_1": "value_2",
                "field_2": 43,
            },
        ]

    def test__missing_key__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {
            "field_1": "string",
            "field_2": 42,
        }
        mock_loader.get.return_value = [
            {
                "field_1": "value_1",
            },
        ]

        with pytest.raises(ParserError) as exception_info:
            parser._parse_item_list(
                key=dummy_key,
                # We are testing here with a simplified expected item type,
                # ignoring the mypy warning.
                expected_item=dummy_expected_item,  # type: ignore
            )

        expected = (
            "Missing mandatory field 'field_2' from section 'my_key' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__additional_key__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {
            "field_1": "string",
            "field_2": 42,
        }
        mock_loader.get.return_value = [
            {
                "field_1": "value_1",
                "field_2": 42,
                "extra_field": "uff",
            },
        ]

        with pytest.raises(ParserError) as exception_info:
            parser._parse_item_list(
                key=dummy_key,
                # We are testing here with a simplified expected item type,
                # ignoring the mypy warning.
                expected_item=dummy_expected_item,  # type: ignore
            )

        expected = (
            "Unexpected field 'extra_field' found for section 'my_key' item at index 1!"
        )
        assert exception_info.match(expected)

    def test__additional_keys__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {
            "field_1": "string",
            "field_2": 42,
        }
        mock_loader.get.return_value = [
            {
                "field_1": "value_1",
                "field_2": 42,
                "extra_field_1": "uff",
                "extra_field_2": "huff",
            },
        ]

        with pytest.raises(ParserError) as exception_info:
            parser._parse_item_list(
                key=dummy_key,
                # We are testing here with a simplified expected item type,
                # ignoring the mypy warning.
                expected_item=dummy_expected_item,  # type: ignore
            )

        expected = "Unexpected fields 'extra_field_1', 'extra_field_2' found for section 'my_key' item at index 1!"
        assert exception_info.match(expected)

    def test__invalid_value_type__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "my_key"
        dummy_expected_item = {
            "field_1": "string",
            "field_2": 42,
        }
        mock_loader.get.return_value = [
            {
                "field_1": "value_1",
                "field_2": "I am not an integer",
            },
        ]

        with pytest.raises(ParserError) as exception_info:
            parser._parse_item_list(
                key=dummy_key,
                # We are testing here with a simplified expected item type,
                # ignoring the mypy warning.
                expected_item=dummy_expected_item,  # type: ignore
            )

        expected = "The value for field 'field_2' should be an int in section 'my_key' item at index 1!"
        assert exception_info.match(expected)
