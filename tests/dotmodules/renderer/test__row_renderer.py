import pytest

from dotmodules.renderer import Colors, RenderError, TableRenderer
from dotmodules.settings import Settings


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def colors():
    return Colors()


@pytest.fixture
def row_renderer(settings, colors):
    return TableRenderer(settings=settings, colors=colors)


class TestColumnWidthCalculationCases:
    def test__column_width_can_be_calculated(self, row_renderer):
        dummy_buffer = [
            ["aaa", "a", "a"],
            ["a", "aaa", "a"],
            ["a", "a", "aaa"],
        ]
        result = row_renderer._calculate_max_column_width(buffer=dummy_buffer)
        assert result == [3, 3, 3]

    def test__inconsistent_columns__error(self, row_renderer):
        dummy_buffer = [
            ["a", "a"],
            ["a"],
        ]
        with pytest.raises(RenderError) as exception_info:
            row_renderer._calculate_max_column_width(buffer=dummy_buffer)
        expected = "inconsistent column count"
        assert expected in str(exception_info.value)


class TestRowRenderingCases:
    def test__rendered_column_width_can_be_adjusted_1(self, settings, row_renderer):
        settings.indent = " " * 4
        settings.column_padding = " " * 2

        row_renderer.add_row("a", "b")
        row_renderer.add_row("aa", "b")
        row_renderer.add_row("aaa", "b")
        result = row_renderer.render(return_lines=True)
        assert result == [
            "    a    b",
            "    aa   b",
            "    aaa  b",
        ]

    def test__rendered_column_width_can_be_adjusted_2(self, settings, row_renderer):
        settings.indent = " " * 2
        settings.column_padding = " " * 1

        row_renderer.add_row("a", "b")
        row_renderer.add_row("aa", "b")
        row_renderer.add_row("aaa", "b")
        result = row_renderer.render(return_lines=True)
        assert result == [
            "  a   b",
            "  aa  b",
            "  aaa b",
        ]

    def test__rendered_column_width_can_be_adjusted_without_indentation(
        self, settings, row_renderer
    ):
        settings.indent = " " * 2
        settings.column_padding = " " * 1

        row_renderer.add_row("a", "b")
        row_renderer.add_row("aa", "b")
        row_renderer.add_row("aaa", "b")
        result = row_renderer.render(return_lines=True, indent=False)
        assert result == [
            "a   b",
            "aa  b",
            "aaa b",
        ]

    def test__coloring_should_not_affect_the_width_adjustment(
        self, settings, row_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 4
        settings.column_padding = " " * 2

        row_renderer.add_row("<<RED>>a<<RESET>>", "<<BLUE>>b<<RESET>>")
        row_renderer.add_row("<<RED>>aa<<RESET>>", "<<BLUE>>b<<RESET>>")
        row_renderer.add_row("<<RED>>aaa<<RESET>>", "<<BLUE>>b<<RESET>>")
        result = row_renderer.render(return_lines=True)

        assert result == [
            "    redareset    bluebreset",
            "    redaareset   bluebreset",
            "    redaaareset  bluebreset",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
                mocker.call(tag="BLUE"),
            ]
        )

    def test__coloring_can_be_added_to_multiple_items_with_indentation(
        self, settings, row_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 2
        settings.column_padding = " " * 1

        row_renderer.add_row(
            "<<BOLD>>[<<RED>>1<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>a<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        row_renderer.add_row(
            "<<BOLD>>[<<RED>>2<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        row_renderer.add_row(
            "<<BOLD>>[<<RED>>3<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aaa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        result = row_renderer.render(
            column_alignments=[
                row_renderer.ALIGN__LEFT,
                row_renderer.ALIGN__RIGHT,
                row_renderer.ALIGN__LEFT,
            ],
            indent=True,
            return_lines=True,
        )

        assert result == [
            "  bold[red1resetbold]reset   yellowareset dimbreset",
            "  bold[red2resetbold]reset  yellowaareset dimbreset",
            "  bold[red3resetbold]reset yellowaaareset dimbreset",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
                mocker.call(tag="YELLOW"),
                mocker.call(tag="DIM"),
            ]
        )

    def test__coloring_can_be_added_to_multiple_items_without_indentation(
        self, settings, row_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 2
        settings.column_padding = " " * 1

        row_renderer.add_row(
            "<<BOLD>>[<<RED>>1<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>a<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        row_renderer.add_row(
            "<<BOLD>>[<<RED>>2<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        row_renderer.add_row(
            "<<BOLD>>[<<RED>>3<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aaa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        result = row_renderer.render(
            column_alignments=[
                row_renderer.ALIGN__LEFT,
                row_renderer.ALIGN__RIGHT,
                row_renderer.ALIGN__LEFT,
            ],
            indent=False,
            return_lines=True,
        )

        assert result == [
            "bold[red1resetbold]reset   yellowareset dimbreset",
            "bold[red2resetbold]reset  yellowaareset dimbreset",
            "bold[red3resetbold]reset yellowaaareset dimbreset",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
                mocker.call(tag="YELLOW"),
                mocker.call(tag="DIM"),
            ]
        )


class TestRowRenderingPrintOutputCases:
    def test__coloring_can_be_added_to_multiple_items_without_indentation(
        self, settings, row_renderer, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 2
        settings.column_padding = " " * 1

        row_renderer.add_row(
            "<<BOLD>>[<<RED>>1<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>a<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        row_renderer.add_row(
            "<<BOLD>>[<<RED>>2<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        row_renderer.add_row(
            "<<BOLD>>[<<RED>>3<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aaa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        row_renderer.render(
            column_alignments=[
                row_renderer.ALIGN__LEFT,
                row_renderer.ALIGN__RIGHT,
                row_renderer.ALIGN__LEFT,
            ],
            indent=False,
        )

        mock_print.assert_has_calls(
            [
                mocker.call("bold[red1resetbold]reset   yellowareset dimbreset"),
                mocker.call("bold[red2resetbold]reset  yellowaareset dimbreset"),
                mocker.call("bold[red3resetbold]reset yellowaaareset dimbreset"),
            ]
        )
        assert mock_print.call_count == 3
        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
                mocker.call(tag="YELLOW"),
                mocker.call(tag="DIM"),
            ]
        )

    def test__coloring_can_be_added_to_multiple_items_with_indentation(
        self, settings, row_renderer, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 2
        settings.column_padding = " " * 1

        row_renderer.add_row(
            "<<BOLD>>[<<RED>>1<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>a<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        row_renderer.add_row(
            "<<BOLD>>[<<RED>>2<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        row_renderer.add_row(
            "<<BOLD>>[<<RED>>3<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aaa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        row_renderer.render(
            column_alignments=[
                row_renderer.ALIGN__LEFT,
                row_renderer.ALIGN__RIGHT,
                row_renderer.ALIGN__LEFT,
            ],
            indent=True,
        )

        mock_print.assert_has_calls(
            [
                mocker.call("  bold[red1resetbold]reset   yellowareset dimbreset"),
                mocker.call("  bold[red2resetbold]reset  yellowaareset dimbreset"),
                mocker.call("  bold[red3resetbold]reset yellowaaareset dimbreset"),
            ]
        )
        assert mock_print.call_count == 3
        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
                mocker.call(tag="YELLOW"),
                mocker.call(tag="DIM"),
            ]
        )
