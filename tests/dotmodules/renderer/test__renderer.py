from pathlib import Path

import pytest

from dotmodules.renderer import Colors, Renderer, RenderError, RowItem
from dotmodules.settings import Settings


@pytest.fixture
def settings():
    return Settings()


class TestRenderItemCases:
    def test__real_length_can_be_calculated(self):
        dummy_value = "a" * 12
        dummy_alignment = "align"
        render_item = RowItem(value=dummy_value, alignment=dummy_alignment)

        assert render_item.width == 12

    def test__real_length_can_be_calculated__value_will_be_stripped(self):
        dummy_value = "    " + "a" * 12 + "  "
        dummy_alignment = "align"
        render_item = RowItem(value=dummy_value, alignment=dummy_alignment)

        assert render_item.width == 12

    def test__item_can_be_rendered__left_align(self):
        dummy_value = "hello"
        dummy_alignment = "{{value:<{width}}}"
        dummy_width = 6
        render_item = RowItem(value=dummy_value, alignment=dummy_alignment)

        assert render_item.render(width=dummy_width) == "hello "


class TestRowRenderingCases:
    def test__column_width_can_be_calculated(self):
        dummy_buffer = [
            [
                RowItem(value="aaa"),
                RowItem(value="a"),
                RowItem(value="a"),
            ],
            [
                RowItem(value="a"),
                RowItem(value="aaa"),
                RowItem(value="a"),
            ],
            [
                RowItem(value="a"),
                RowItem(value="a"),
                RowItem(value="aaa"),
            ],
        ]
        result = Renderer._calculate_max_column_width(buffer=dummy_buffer)
        assert result == [3, 3, 3]

    def test__inconsistent_columns__error(self):
        dummy_buffer = [
            [
                RowItem(value="a"),
                RowItem(value="a"),
            ],
            [
                RowItem(value="a"),
            ],
        ]
        with pytest.raises(RenderError) as exception_info:
            Renderer._calculate_max_column_width(buffer=dummy_buffer)
        expected = "inconsistent column count"
        assert expected in str(exception_info.value)

    def test__width_can_be_adjusted(self, settings, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")

        settings.indent = " " * 4
        settings.column_padding = " " * 2

        renderer = Renderer(settings=settings)
        renderer.add_row(
            values=[
                "a",
                "b",
            ],
            alignments=[
                renderer.row.ALIGN__LEFT,
                renderer.row.ALIGN__LEFT,
            ],
        )
        renderer.add_row(
            values=[
                "aa",
                "b",
            ],
            alignments=[
                renderer.row.ALIGN__LEFT,
                renderer.row.ALIGN__LEFT,
            ],
        )
        renderer.add_row(
            values=[
                "aaa",
                "b",
            ],
            alignments=[
                renderer.row.ALIGN__LEFT,
                renderer.row.ALIGN__LEFT,
            ],
        )
        renderer.commit_rows()
        expected_calls = [
            mocker.call("    a    b"),
            mocker.call("    aa   b"),
            mocker.call("    aaa  b"),
        ]
        mock_print.assert_has_calls(expected_calls)


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
    def test__tag_recognition_and_cleaning(self, input_string: str, expected: str):
        result = Colors.clean(string=input_string)
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
    def test__tag_list_collection(self, input_string: str, expected: str):
        result = Colors._get_tag_list(string=input_string)
        assert result == expected


class TestColorCacheHandlingCases:
    def test__missing_color_can_be_filled(self, mocker):
        dummy_tag = "my_tag"
        dummy_color = "my_color"
        mock_load_color = mocker.patch("dotmodules.renderer.Colors._load_color_for_tag")
        mock_load_color.return_value = dummy_color

        assert Colors.color_cache == {}
        Colors._update_color_cache(tags=[dummy_tag])
        assert Colors.color_cache == {dummy_tag: dummy_color}

        mock_load_color.assert_called_with(tag=dummy_tag)

    def test__existing_tag_wont_be_resolved(self, mocker):
        dummy_tag = "my_tag"
        dummy_color = "my_color"
        mock_load_color = mocker.patch("dotmodules.renderer.Colors._load_color_for_tag")
        mock_load_color.return_value = dummy_color

        assert Colors.color_cache == {dummy_tag: dummy_color}
        Colors._update_color_cache(tags=[dummy_tag])
        assert Colors.color_cache == {dummy_tag: dummy_color}

        mock_load_color.assert_not_called


class TestColorLoadingCommandAssemlingCases:
    def test__mapped_tag__command_should_be_the_mapping(self):
        dummy_tag = "my_tag"
        dummy_mapped_tag = "my_mapped_tag"
        Colors.tag_mapping[dummy_tag] = dummy_mapped_tag

        expected_command = Colors.command + [dummy_mapped_tag]

        result = Colors._assemble_color_loading_command(tag=dummy_tag)

        assert result == expected_command

        # Have to remove the change in the class variable.
        Colors.tag_mapping.pop(dummy_tag)

    def test__unmapped_tag__gets_loaded_with_a_default_template(self, mocker):
        dummy_tag = "123"

        expected_command = Colors.command + ["setaf", dummy_tag]

        result = Colors._assemble_color_loading_command(tag=dummy_tag)

        assert result == expected_command

    def test__unmapped_tag__has_to_be_a_number(self, mocker):
        dummy_tag = "my_non_numeric_tag"

        with pytest.raises(ValueError) as e:
            Colors._assemble_color_loading_command(tag=dummy_tag)

        expected = "unmapped tag has to be numeric: 'my_non_numeric_tag'"
        assert str(e.value) == expected


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

    def test__colors_can_be_fetched__success(self, dummy_color_adapter, mocker):
        dummy_tag = "my_tag"
        dummy_command = [dummy_color_adapter, "--success", dummy_tag]
        mock_assemble_command = mocker.patch(
            "dotmodules.renderer.Colors._assemble_color_loading_command"
        )
        mock_assemble_command.return_value = dummy_command

        result = Colors._load_color_for_tag(tag=dummy_tag)

        assert result == dummy_tag
        mock_assemble_command.assert_called_with(tag=dummy_tag)

    def test__colors_can_be_fetched__error__graceful_handling(
        self, dummy_color_adapter, mocker
    ):
        dummy_tag = "my_tag"
        dummy_command = [dummy_color_adapter, "--error"]
        mock_assemble_command = mocker.patch(
            "dotmodules.renderer.Colors._assemble_color_loading_command"
        )
        mock_assemble_command.return_value = dummy_command

        result = Colors._load_color_for_tag(tag=dummy_tag)

        # Cannot resolve tag -> returns no coloring.
        assert result == ""
        mock_assemble_command.assert_called_with(tag=dummy_tag)


class TestColororizeCases:
    @pytest.fixture(autouse=True)
    def setup(self):
        Colors.color_cache = {}

    def test__no_color_tags(self):
        dummy_string = "I am a dummy string with no colors"
        result = Colors.colorize(string=dummy_string)
        assert result == dummy_string

    def test__color_tags_can_be_resolved(self, mocker):
        dummy_string = "<<RED>>I am in color<<RESET>>"
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.Colors._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        result = Colors.colorize(string=dummy_string)

        # The mocked color loading simply converts the tag names into lowercase.
        assert result == "redI am in colorreset"

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__repeated_color_tags_can_be_resolved(self, mocker):
        dummy_string = "<<RED>>I am in <<RED>>color<<RESET>>"
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.Colors._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        result = Colors.colorize(string=dummy_string)

        # The mocked color loading simply converts the tag names into lowercase.
        assert result == "redI am in redcolorreset"

        # The cache is only updated twice.
        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
            ]
        )
