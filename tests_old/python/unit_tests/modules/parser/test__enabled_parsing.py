import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.loader import LoaderError
from dotmodules.modules.parser import ConfigParser, ParserError


class TestEnabledParsing:
    def test__missing_definition(
        self,
        parser: ConfigParser,
        mocker: MockerFixture,
    ) -> None:
        mock_parse_boolean = mocker.patch.object(parser.loader, "get")
        mock_parse_boolean.side_effect = LoaderError("my error")

        with pytest.raises(ParserError) as error_context:
            parser.parse_enabled(deployment_target="")

        expected_error_message = "Mandatory section 'enabled' is missing!"
        assert error_context.match(expected_error_message)

        mock_parse_boolean.assert_called_with(key="enabled")

    @pytest.mark.parametrize(
        "value, expected",
        [
            [True, True],
            [False, False],
        ],
    )
    def test__global__valid_value__no_deployment_target(
        self,
        parser: ConfigParser,
        mocker: MockerFixture,
        value: bool,
        expected: bool,
    ) -> None:
        mock_parse_boolean = mocker.patch.object(parser.loader, "get")
        mock_parse_boolean.return_value = value

        result = parser.parse_enabled(deployment_target="")
        assert result == expected

        mock_parse_boolean.assert_called_with(key="enabled")

    @pytest.mark.parametrize(
        "value, expected",
        [
            [True, True],
            [False, False],
        ],
    )
    def test__global__valid_value__deployment_target_specified(
        self,
        parser: ConfigParser,
        mocker: MockerFixture,
        value: bool,
        expected: bool,
    ) -> None:
        mock_parse_boolean = mocker.patch.object(parser.loader, "get")
        mock_parse_boolean.return_value = value

        # Having a deployment target specified shouldn't change the global
        # definition's outcome.
        result = parser.parse_enabled(deployment_target="some_target")
        assert result == expected

        mock_parse_boolean.assert_called_with(key="enabled")

    @pytest.mark.parametrize(
        "value",
        ["invalid", 42, []],
    )
    def test__global__invalid_value(
        self,
        parser: ConfigParser,
        mocker: MockerFixture,
        value: bool,
    ) -> None:
        mock_parse_boolean = mocker.patch.object(parser.loader, "get")
        mock_parse_boolean.return_value = value

        with pytest.raises(ParserError) as error_context:
            parser.parse_enabled(deployment_target="")

        expected_error_message = f"The value for section 'enabled' should be boolean, got {type(value).__name__}!"
        assert error_context.match(expected_error_message)

        mock_parse_boolean.assert_called_with(key="enabled")

    @pytest.mark.parametrize(
        "value, expected",
        [
            [True, True],
            [False, False],
        ],
    )
    def test__deployment_target_specific__valid_values(
        self,
        parser: ConfigParser,
        mocker: MockerFixture,
        value: bool,
        expected: bool,
    ) -> None:
        dummy_deployment_target = "my_target"
        mock_parse_boolean = mocker.patch.object(parser.loader, "get")
        mock_parse_boolean.return_value = {
            dummy_deployment_target: value,
            "other_deployment_target": False,
        }

        result = parser.parse_enabled(deployment_target=dummy_deployment_target)
        assert result == expected

        mock_parse_boolean.assert_called_with(key="enabled")

    @pytest.mark.parametrize(
        "value",
        ["invalid", 42, []],
    )
    def test__deployment_target_specific__invalid_value(
        self,
        parser: ConfigParser,
        mocker: MockerFixture,
        value: bool,
    ) -> None:
        dummy_deployment_target = "my_target"
        mock_parse_boolean = mocker.patch.object(parser.loader, "get")
        mock_parse_boolean.return_value = {
            dummy_deployment_target: value,
            "other_deployment_target": False,
        }

        with pytest.raises(ParserError) as error_context:
            parser.parse_enabled(deployment_target=dummy_deployment_target)

        expected_error_message = (
            f"The value for section 'enabled' should be boolean for deployment "
            f"target '{dummy_deployment_target}', got {type(value).__name__}!"
        )
        assert error_context.match(expected_error_message)

        mock_parse_boolean.assert_called_with(key="enabled")

    def test__deployment_target_specific__missing_deployment_target(
        self,
        parser: ConfigParser,
        mocker: MockerFixture,
    ) -> None:
        dummy_deployment_target = "my_target"
        mock_parse_boolean = mocker.patch.object(parser.loader, "get")

        # NOTE: that the given deployment target is missing.
        mock_parse_boolean.return_value = {
            "other_deployment_target": False,
        }

        with pytest.raises(ParserError) as error_context:
            parser.parse_enabled(deployment_target=dummy_deployment_target)

        expected_error_message = f"Missing deployment target '{dummy_deployment_target}' from section 'enabled'!"
        assert error_context.match(expected_error_message)

        mock_parse_boolean.assert_called_with(key="enabled")

    def test__deployment_target_specific_only__no_deployment_target(
        self,
        parser: ConfigParser,
        mocker: MockerFixture,
    ) -> None:
        dummy_deployment_target = ""
        mock_parse_boolean = mocker.patch.object(parser.loader, "get")

        mock_parse_boolean.return_value = {
            "other_deployment_target": False,
        }

        with pytest.raises(ParserError) as error_context:
            parser.parse_enabled(deployment_target=dummy_deployment_target)

        expected_error_message = (
            "Section 'enabled' was defined for deployment targets only, but "
            "there is no deployment target specified for the current deployment!"
        )
        assert error_context.match(expected_error_message)

        mock_parse_boolean.assert_called_with(key="enabled")
