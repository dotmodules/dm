from typing import Dict, List
from unittest.mock import MagicMock

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.loader import LoaderError
from dotmodules.modules.parser import ConfigParser, ParserError


class TestVariablesLoading:
    def test__load_missing_global_variables(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        mock_loader.get.side_effect = LoaderError("missing key!")

        result = parser._load_global_variables()
        assert result == {}

        mock_loader.get.assert_called_once_with(key="variables")

    def test__load_global_variables(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        mock_loader.get.return_value = "some_object"

        result = parser._load_global_variables()
        assert result == "some_object"

        mock_loader.get.assert_called_once_with(key="variables")

    def test__load_missing_deployment_target_variables_variables(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_deployment_target = "my_target"
        mock_loader.get.side_effect = LoaderError("missing key!")

        result = parser._load_deployment_target_variables(
            deployment_target=dummy_deployment_target
        )
        assert result == {}

        mock_loader.get.assert_called_once_with(
            key=f"variables__{dummy_deployment_target}"
        )

    def test__load_deployment_target_variables(
        self, parser: ConfigParser, mock_loader: MagicMock
    ) -> None:
        dummy_deployment_target = "my_target"
        mock_loader.get.return_value = "some_object"

        result = parser._load_deployment_target_variables(
            deployment_target=dummy_deployment_target
        )
        assert result == "some_object"

        mock_loader.get.assert_called_once_with(
            key=f"variables__{dummy_deployment_target}"
        )


class TestVariablesParsing:
    def test__missing_global_variables__without_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(parser, "_load_global_variables", return_value={})
        mock_load_deployment_target_variables = mocker.patch.object(
            parser, "_load_deployment_target_variables", return_value={}
        )

        result = parser.parse_variables(deployment_target="")
        assert result == {}

        mock_load_deployment_target_variables.assert_not_called()

    def test__missing_global_variables__with_missing_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"

        mocker.patch.object(parser, "_load_global_variables", return_value={})
        mock_load_deployment_target_variables = mocker.patch.object(
            parser, "_load_deployment_target_variables", return_value={}
        )

        result = parser.parse_variables(deployment_target=dummy_deployment_target)
        assert result == {}

        mock_load_deployment_target_variables.assert_called_once_with(
            deployment_target=dummy_deployment_target
        )

    def test__missing_global_variables__with_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"

        mocker.patch.object(parser, "_load_global_variables", return_value={})
        mock_load_deployment_target_variables = mocker.patch.object(
            parser,
            "_load_deployment_target_variables",
            return_value={"DEPLOYMENT": ["value_3", "value_4"]},
        )

        result = parser.parse_variables(deployment_target=dummy_deployment_target)
        assert result == {"DEPLOYMENT": ["value_3", "value_4"]}

        mock_load_deployment_target_variables.assert_called_once_with(
            deployment_target=dummy_deployment_target
        )

    def test__global_variables__without_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        mocker.patch.object(
            parser,
            "_load_global_variables",
            return_value={"GLOBAL": ["value_1", "value_2"]},
        )
        mock_load_deployment_target_variables = mocker.patch.object(
            parser, "_load_deployment_target_variables", return_value={}
        )

        result = parser.parse_variables(deployment_target="")
        assert result == {"GLOBAL": ["value_1", "value_2"]}

        mock_load_deployment_target_variables.assert_not_called()

    def test__global_variables__with_missing_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"

        mocker.patch.object(
            parser,
            "_load_global_variables",
            return_value={"GLOBAL": ["value_1", "value_2"]},
        )
        mock_load_deployment_target_variables = mocker.patch.object(
            parser, "_load_deployment_target_variables", return_value={}
        )

        result = parser.parse_variables(deployment_target=dummy_deployment_target)
        assert result == {"GLOBAL": ["value_1", "value_2"]}

        mock_load_deployment_target_variables.assert_called_once_with(
            deployment_target=dummy_deployment_target
        )

    def test__global_variables__with_deployment_target(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"

        mocker.patch.object(
            parser,
            "_load_global_variables",
            return_value={"GLOBAL": ["value_1", "value_2"]},
        )
        mock_load_deployment_target_variables = mocker.patch.object(
            parser,
            "_load_deployment_target_variables",
            return_value={"DEPLOYMENT": ["value_3", "value_4"]},
        )

        result = parser.parse_variables(deployment_target=dummy_deployment_target)
        assert result == {
            "GLOBAL": ["value_1", "value_2"],
            "DEPLOYMENT": ["value_3", "value_4"],
        }

        mock_load_deployment_target_variables.assert_called_once_with(
            deployment_target=dummy_deployment_target
        )

    def test__deployment_target_redefines_key(
        self, parser: ConfigParser, mocker: MockerFixture
    ) -> None:
        dummy_deployment_target = "my_target"

        mocker.patch.object(
            parser,
            "_load_global_variables",
            return_value={"SAME_KEY": ["value_1", "value_2"]},
        )
        mock_load_deployment_target_variables = mocker.patch.object(
            parser,
            "_load_deployment_target_variables",
            return_value={"SAME_KEY": ["value_3", "value_4"]},
        )

        with pytest.raises(ParserError) as error_context:
            parser.parse_variables(deployment_target=dummy_deployment_target)

        expected_error_message = (
            "Deployment target specific variable section "
            f"'variables__{dummy_deployment_target}' redefined already existing global "
            "variable key 'SAME_KEY'!"
        )

        assert error_context.match(expected_error_message)

        mock_load_deployment_target_variables.assert_called_once_with(
            deployment_target=dummy_deployment_target
        )


class TestValidateVariablesParsing:
    def test__empty_dict__should_be_left_as_is(self, parser: ConfigParser) -> None:
        dummy_variables: Dict[str, List[str]] = {}

        result = parser._validate_variables(variables=dummy_variables)
        assert result == {}

    def test__scalar_value__error_should_be_raised(self, parser: ConfigParser) -> None:
        dummy_variables = "I am a string"

        with pytest.raises(ParserError) as exception_info:
            parser._validate_variables(variables=dummy_variables)

        expected = r"The 'variables' section should have the following syntax: 'VARIABLE_NAME' = \['var_1', 'var_2', \.\.\] !"
        assert exception_info.match(expected)

    def test__non_compatible_variable__error_should_be_raised(
        self, parser: ConfigParser
    ) -> None:
        dummy_variables = {
            "VARIABLE": {"this is not a list": 42},
        }
        with pytest.raises(ParserError) as exception_info:
            parser._validate_variables(variables=dummy_variables)

        expected = "The 'variables' section should contain a single string or a list of strings for a variable name!"
        assert exception_info.match(expected)

    def test__non_list_variable_value__should_be_converted_to_a_list(
        self, parser: ConfigParser
    ) -> None:
        dummy_variables = {
            "VARIABLE": "I am not a list",
        }
        result = parser._validate_variables(variables=dummy_variables)

        assert result == {
            "VARIABLE": ["I am not a list"],
        }

    def test__list_variable_values__should_be_left_as_is(
        self, parser: ConfigParser
    ) -> None:
        dummy_variables = {
            "VARIABLE": ["I", "am", "a", "list"],
        }
        result = parser._validate_variables(variables=dummy_variables)
        assert result == {
            "VARIABLE": ["I", "am", "a", "list"],
        }

    def test__non_string_items__error_should_be_raised(
        self, parser: ConfigParser
    ) -> None:
        dummy_variables = {
            "VARIABLE": ["I am a string", 42],
        }
        with pytest.raises(ParserError) as exception_info:
            parser._validate_variables(variables=dummy_variables)

        expected = "The 'variables' section should contain a single string or a list of strings for a variable name!"
        assert exception_info.match(expected)
