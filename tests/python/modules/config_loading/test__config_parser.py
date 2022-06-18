from typing import cast
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.loader import ConfigLoader, LoaderError
from dotmodules.modules.parser import ConfigParser, ParserError


@pytest.fixture
def mock_loader(mocker: MockerFixture) -> MagicMock:
    # By default the type of a MagicMock object is Any. We want to narrow it
    # back to MagicMock..
    return cast(MagicMock, mocker.MagicMock())


@pytest.fixture
def parser(mocker: MockerFixture, mock_loader: MagicMock) -> ConfigParser:
    loader = cast(ConfigLoader, mock_loader)
    return ConfigParser(loader=loader)


# =============================================================================
#  LOW LEVEL PARSING METHODS
# =============================================================================


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
        assert str(exception_info.value) == expected

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
        assert str(exception_info.value) == expected

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

        expected = f"Value for section '{dummy_key}' should be a string, got '['this', 'is', 'not', 'a', 'string']'!"
        assert str(exception_info.value) == expected

        mock_loader.get.assert_called_with(key=dummy_key)


class TestBooleanParsing:
    def test__valid_boolean_can_be_parsed(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "key"
        dummy_value = True
        mock_loader.get.return_value = dummy_value

        result = parser._parse_boolean(key=dummy_key)
        assert result == dummy_value

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__missing_key__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "invalid_key"
        mock_loader.get.side_effect = LoaderError("missing key")

        with pytest.raises(ParserError) as exception_info:
            parser._parse_boolean(key=dummy_key)

        expected = f"Mandatory '{dummy_key}' section is missing!"
        assert str(exception_info.value) == expected

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__missing_key__but_not_mandatory__false_should_be_returned(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_key = "invalid_key"
        mock_loader.get.side_effect = LoaderError("missing key")

        result = parser._parse_boolean(key=dummy_key, mandatory=False)

        assert not result

        mock_loader.get.assert_called_with(key=dummy_key)

    def test__non_boolean_value__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_value = 42
        dummy_key = "key"
        mock_loader.get.return_value = dummy_value

        with pytest.raises(ParserError) as exception_info:
            parser._parse_boolean(key=dummy_key)

        expected = f"Value for section '{dummy_key}' should be a boolean, got '42'!"
        assert str(exception_info.value) == expected

        mock_loader.get.assert_called_with(key=dummy_key)


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
        assert str(exception_info.value) == expected

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
        assert str(exception_info.value) == expected

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
        assert str(exception_info.value) == expected

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
        assert str(exception_info.value) == expected

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
        assert str(exception_info.value) == expected

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
        assert str(exception_info.value) == expected


# =============================================================================
#  HIGHER LEVEL PARSING METHODS
# =============================================================================


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


class TestEnabledParsing:
    def test__enabled_flag_can_be_parsed(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_enabled_flag = True
        mock_parse_boolean = mocker.patch.object(parser, "_parse_boolean")
        mock_parse_boolean.return_value = dummy_enabled_flag

        result = parser.parse_enabled()
        assert result == dummy_enabled_flag

        mock_parse_boolean.assert_called_with(key="enabled")


class TestDocumentationParsing:
    def test__documentation_can_be_parsed(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_documentation = "line1\nline2"
        mock_parse_string = mocker.patch.object(parser, "_parse_string")
        mock_parse_string.return_value = dummy_documentation

        result = parser.parse_documentation()
        assert result == [
            "line1",
            "line2",
        ]

        mock_parse_string.assert_called_with(key="documentation", mandatory=False)


class TestVariablesParsing:
    def test__missing_key_should_be_converted_to_dict(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        mock_loader.get.side_effect = LoaderError("missing key")

        result = parser.parse_variables()
        assert result == {}

        mock_loader.get.assert_called_with(key="variables")

    def test__empty_value_should_be_left_as_is(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        mock_loader.get.return_value = {}

        result = parser.parse_variables()
        assert result == {}

        mock_loader.get.assert_called_with(key="variables")

    def test__scalar_value__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        mock_loader.get.return_value = "I am a string"

        with pytest.raises(ParserError) as exception_info:
            parser.parse_variables()

        expected = "The 'variables' section should have the following syntax: 'VARIABLE_NAME' = ['var_1', 'var_2', ..] !"
        assert str(exception_info.value) == expected

        mock_loader.get.assert_called_with(key="variables")

    def test__non_string_key__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        mock_loader.get.return_value = {
            42: ["non", "string", "key"],
        }

        with pytest.raises(ParserError) as exception_info:
            parser.parse_variables()

        expected = "The 'variables' section should only have string variable names!"
        assert str(exception_info.value) == expected

        mock_loader.get.assert_called_with(key="variables")

    def test__non_compatible_variable__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        mock_loader.get.return_value = {
            "VARIABLE": {"this is not a list": 42},
        }
        with pytest.raises(ParserError) as exception_info:
            parser.parse_variables()

        expected = "The 'variables' section should contain a single string or a list of strings for a variable name!"
        assert str(exception_info.value) == expected

        mock_loader.get.assert_called_with(key="variables")

    def test__non_list_variable_value__should_be_converted_to_a_list(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        mock_loader.get.return_value = {
            "VARIABLE": "I am not a list",
        }
        result = parser.parse_variables()
        assert result == {
            "VARIABLE": ["I am not a list"],
        }

        mock_loader.get.assert_called_with(key="variables")

    def test__list_variable_values__should_be_left_as_is(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        mock_loader.get.return_value = {
            "VARIABLE": ["I", "am", "a", "list"],
        }
        result = parser.parse_variables()
        assert result == {
            "VARIABLE": ["I", "am", "a", "list"],
        }

        mock_loader.get.assert_called_with(key="variables")

    def test__non_string_items__error_should_be_raised(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        mock_loader.get.return_value = {
            "VARIABLE": ["I am a string", 42],
        }
        with pytest.raises(ParserError) as exception_info:
            parser.parse_variables()

        expected = "The 'variables' section should contain a single string or a list of strings for a variable name!"
        assert str(exception_info.value) == expected

        mock_loader.get.assert_called_with(key="variables")


class TestLinkParsing:
    def test__links_can_be_parsed(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_links = [
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
        mock_parse_item_list.return_value = dummy_links

        result = parser.parse_links()
        assert result == dummy_links

        mock_parse_item_list.assert_called_with(
            key="links",
            expected_item={
                "path_to_target": "string",
                "path_to_symlink": "string",
                "name": "string",
            },
        )


class TestHookParsing:
    def test__hooks_can_be_parsed(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_hooks = [
            {
                "path_to_script": "my_path_to_script_1",
                "name": "my_name_1",
                "priority": 42,
            },
            {
                "path_to_script": "my_path_to_script_2",
                "name": "my_name_2",
                "priority": 43,
            },
        ]
        mock_parse_item_list = mocker.patch.object(parser, "_parse_item_list")
        mock_parse_item_list.return_value = dummy_hooks

        result = parser.parse_hooks()
        assert result == dummy_hooks

        mock_parse_item_list.assert_called_with(
            key="hooks",
            expected_item={
                "path_to_script": "string",
                "name": "string",
                "priority": 0,
            },
        )
