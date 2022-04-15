from pathlib import Path

import pytest

from dotmodules.renderer import ColorAdapter, Colors


@pytest.fixture
def colors():
    return Colors()


@pytest.fixture
def coloring_tag_cache():
    return ColorAdapter()


class TestColorTagRecognitionCases:
    @pytest.mark.parametrize(
        "input_string,expected",
        [
            ["<<TAG>>", ""],  # Tags should be uppercase only.
            ["<<Tag>>", "<<Tag>>"],  # Tags should be uppercase only.
            ["<<a1>>", "<<a1>>"],  # Tags should be either alphanumeric or numeric.
            ["<<A1>>", "<<A1>>"],  # Tags should be either alphanumeric or numeric.
            ["<<A-2>>", "<<A-2>>"],  # Tags should contain only letters and numbers.
            ["<<1>>", ""],  # Single numbers are allowed.
            ["<<12>>", ""],  # Double numbers are allowed.
            ["<<123>>", ""],  # Maximum three numbers are allowed.
            ["<<1234>>", "<<1234>>"],  # Maximum three numbers are allowed.
            ["<tag>", "<tag>"],  # A tag should be anclosed into double angle brackets.
            ["<TAG>", "<TAG>"],  # A tag should be anclosed into double angle brackets.
            ["abc", "abc"],  # Double angle brackets are necessary.
            ["ABC", "ABC"],  # Double angle brackets are necessary.
            ["123", "123"],  # Double angle brackets are necessary.
            ["-.,<>:;", "-.,<>:;"],  # Double angle brackets are necessary.
            ["<<>>", "<<>>"],  # Empty double angle brackets are not considered as tags.
            ["<< >>", "<< >>"],  # Whitespace is not a tag.
            ["<<<<TAG>>", "<<"],  # Surrounding whitespace in not a requirement.
            ["<< <<TAG>>", "<< "],  # Surrounding whitespace in not a requirement.
            ["<<TAG>>>>", ">>"],  # Surrounding whitespace in not a requirement.
            ["<<TAG>> >>", " >>"],  # Surrounding whitespace in not a requirement.
            ["<<A>>hello<<B>>", "hello"],  # Multiple tags are supported.
        ],
    )
    def test__tag_recognition_and_cleaning(
        self, input_string: str, expected: str, colors
    ):
        result = colors.decolor_string(string=input_string)
        assert result == expected

    @pytest.mark.parametrize(
        "input_string,expected",
        [
            ["<<TAG>>", ("TAG",)],  # Tags should be uppercase only.
            ["<<Tag>>", None],  # Tags should be uppercase only.
            ["<<abc123>>", None],  # Tags should be either alphanumeric or numeric.
            ["<<ABC123>>", None],  # Tags should be either alphanumeric or numeric.
            ["<<A-2>>", None],  # Tags should contain only letters and numbers.
            ["<<1>>", ("1",)],  # Single numbers are allowed.
            ["<<12>>", ("12",)],  # Double numbers are allowed.
            ["<<123>>", ("123",)],  # Maximum three numbers are allowed.
            ["<<1234>>", None],  # Maximum three numbers are allowed.
            ["<tag>", None],  # A tag should be anclosed into double angle brackets.
            ["<TAG>", None],  # A tag should be anclosed into double angle brackets.
            ["abc", None],  # Double angle brackets are necessary.
            ["ABC", None],  # Double angle brackets are necessary.
            ["123", None],  # Double angle brackets are necessary.
            ["-.,<>:;", None],  # Double angle brackets are necessary.
            ["<<>>", None],  # Empty double angle brackets are not considered as tags.
            ["<< >>", None],  # Whitespace is not a tag.
            ["<<<<TAG>>", ("TAG",)],  # Surrounding whitespace in not a requirement.
            ["<< <<TAG>>", ("TAG",)],  # Surrounding whitespace in not a requirement.
            ["<<TAG>>>>", ("TAG",)],  # Surrounding whitespace in not a requirement.
            ["<<TAG>> >>", ("TAG",)],  # Surrounding whitespace in not a requirement.
            ["<<A>>hello<<B>>", ("A", "B")],  # Multiple tags are supported.
        ],
    )
    def test__tag_list_collection(self, input_string: str, expected: str, colors):
        result = colors._get_tag_list(string=input_string)
        assert result == expected


class TestColorCacheHandlingCases:
    def test__missing_color_can_be_filled(self, mocker, coloring_tag_cache):
        dummy_tag = "my_tag"
        dummy_color = "my_color"
        mock_load_color = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag"
        )
        mock_load_color.return_value = dummy_color

        assert coloring_tag_cache._cache == {}
        result = coloring_tag_cache.resolve_tag(tag=dummy_tag)
        assert result == dummy_color
        assert coloring_tag_cache._cache == {dummy_tag: dummy_color}

        mock_load_color.assert_called_with(tag=dummy_tag)

    def test__existing_tag_wont_be_resolved(self, mocker, coloring_tag_cache):
        dummy_tag = "my_tag"
        dummy_color = "my_color"
        mock_load_color = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag"
        )
        coloring_tag_cache._cache[dummy_tag] = dummy_color

        assert coloring_tag_cache._cache == {dummy_tag: dummy_color}
        result = coloring_tag_cache.resolve_tag(tag=dummy_tag)
        assert result == dummy_color
        assert coloring_tag_cache._cache == {dummy_tag: dummy_color}

        mock_load_color.assert_not_called


class TestColorLoadingCommandAssemlingCases:
    def test__mapped_tag__command_should_be_the_mapping(self, coloring_tag_cache):
        dummy_tag = "my_tag"
        dummy_mapped_tag = "my_mapped_tag"
        coloring_tag_cache.TAG_MAPPING[dummy_tag] = dummy_mapped_tag

        expected_command = ["utils/color_adapter.sh", dummy_mapped_tag]

        result = coloring_tag_cache._assemble_color_loading_command(tag=dummy_tag)

        assert result == expected_command

    def test__unmapped_tag__gets_loaded_with_a_default_template(
        self, coloring_tag_cache
    ):
        dummy_tag = "123"

        expected_command = ["utils/color_adapter.sh", "setaf", dummy_tag]

        result = coloring_tag_cache._assemble_color_loading_command(tag=dummy_tag)

        assert result == expected_command

    def test__unmapped_tag__has_to_be_a_number(self, coloring_tag_cache):
        dummy_tag = "my_non_numeric_tag"

        with pytest.raises(ValueError) as e:
            coloring_tag_cache._assemble_color_loading_command(tag=dummy_tag)

        expected = "unmapped tag has to be numeric: 'my_non_numeric_tag'"
        assert str(e.value) == expected

    def test__mapped_tag__multiple_commands_can_be_generated(self, coloring_tag_cache):
        dummy_tag_1 = "my_tag"
        dummy_tag_2 = "my_tag"
        dummy_mapped_tag_1 = "my_mapped_tag"
        dummy_mapped_tag_2 = "my_mapped_tag"
        coloring_tag_cache.TAG_MAPPING[dummy_tag_1] = dummy_mapped_tag_1
        coloring_tag_cache.TAG_MAPPING[dummy_tag_2] = dummy_mapped_tag_2

        expected_command_1 = ["utils/color_adapter.sh", dummy_mapped_tag_1]
        expected_command_2 = ["utils/color_adapter.sh", dummy_mapped_tag_2]

        result_1 = coloring_tag_cache._assemble_color_loading_command(tag=dummy_tag_1)
        result_2 = coloring_tag_cache._assemble_color_loading_command(tag=dummy_tag_2)

        assert result_1 == expected_command_1
        assert result_2 == expected_command_2


class TestColorLoadingCases:
    @pytest.fixture()
    def dummy_color_adapter(self) -> str:
        """
        Dummy loader script that can be called in two modes:

        > dummy_color_adapter.sh --success <message>
        In this mode the passed <message> will be echoed back.

        > dummy_color_adapter.sh --error
        In this mode the script will abort with an error.
        """
        return str(Path(__file__).parent / "dummy_color_adapter.sh")

    def test__colors_can_be_fetched__success(
        self, dummy_color_adapter, mocker, coloring_tag_cache
    ):
        dummy_tag = "my_tag"
        dummy_command = [dummy_color_adapter, "--success", dummy_tag]
        mock_assemble_command = mocker.patch(
            "dotmodules.renderer.ColorAdapter._assemble_color_loading_command"
        )
        mock_assemble_command.return_value = dummy_command

        result = coloring_tag_cache._load_color_for_tag(tag=dummy_tag)

        assert result == dummy_tag
        mock_assemble_command.assert_called_with(tag=dummy_tag)

    def test__colors_can_be_fetched__error__graceful_handling(
        self, dummy_color_adapter, mocker, coloring_tag_cache
    ):
        dummy_tag = "my_tag"
        dummy_command = [dummy_color_adapter, "--error"]
        mock_assemble_command = mocker.patch(
            "dotmodules.renderer.ColorAdapter._assemble_color_loading_command"
        )
        mock_assemble_command.return_value = dummy_command

        result = coloring_tag_cache._load_color_for_tag(tag=dummy_tag)

        # Cannot resolve tag -> returns no coloring.
        assert result == ""
        mock_assemble_command.assert_called_with(tag=dummy_tag)


class TestColororizeCases:
    def test__no_color_tags(self, colors):
        dummy_string = "I am a dummy string with no colors"
        result = colors.colorize(string=dummy_string)
        assert result.colorized_string == dummy_string
        assert result.additional_width == 0

    def test__color_tags_can_be_resolved(self, mocker, colors):
        dummy_string = "<<RED>>I am in color<<RESET>>"
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        result = colors.colorize(string=dummy_string)

        # The mocked color loading simply converts the tag names into lowercase.
        assert result.colorized_string == "redI am in colorreset"
        assert result.additional_width == 8

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__repeated_color_tags_can_be_resolved(self, mocker, colors):
        dummy_string = "<<RED>>I am in <<RED>>color<<RESET>>"
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        result = colors.colorize(string=dummy_string)

        # The mocked color loading simply converts the tag names into lowercase.
        assert result.colorized_string == "redI am in redcolorreset"
        assert result.additional_width == 11

        # The cache is only updated twice.
        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
            ]
        )
