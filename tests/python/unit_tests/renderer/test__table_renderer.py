import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.renderer import Colors, RenderError, TableRenderer
from dotmodules.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def colors() -> Colors:
    return Colors()


@pytest.fixture
def table_renderer(settings: Settings, colors: Colors) -> TableRenderer:
    return TableRenderer(settings=settings, colors=colors)


class TestColumnWidthCalculationCases:
    def test__column_width_can_be_calculated(
        self, table_renderer: TableRenderer
    ) -> None:
        dummy_buffer = [
            ["aaa", "a", "a"],
            ["a", "aaa", "a"],
            ["a", "a", "aaa"],
        ]
        result = table_renderer._calculate_max_column_width(buffer=dummy_buffer)
        assert result == [3, 3, 3]

    def test__inconsistent_columns__error(self, table_renderer: TableRenderer) -> None:
        dummy_buffer = [
            ["a", "a"],
            ["a"],
        ]
        with pytest.raises(RenderError) as exception_info:
            table_renderer._calculate_max_column_width(buffer=dummy_buffer)
        expected = ".*inconsistent column count.*"
        assert exception_info.match(expected)


class TestRowRenderingCases:
    def test__rendered_column_width_can_be_adjusted_1(
        self, settings: Settings, table_renderer: TableRenderer
    ) -> None:
        settings.indent = " " * 4
        settings.column_padding = " " * 2

        table_renderer.add_row("a", "b")
        table_renderer.add_row("aa", "b")
        table_renderer.add_row("aaa", "b")
        result = table_renderer.render(print_lines=False)
        assert result == [
            "    a    b",
            "    aa   b",
            "    aaa  b",
        ]

    def test__rendered_column_width_can_be_adjusted_2(
        self, settings: Settings, table_renderer: TableRenderer
    ) -> None:
        settings.indent = " " * 2
        settings.column_padding = " " * 1

        table_renderer.add_row("a", "b")
        table_renderer.add_row("aa", "b")
        table_renderer.add_row("aaa", "b")
        result = table_renderer.render(print_lines=False)
        assert result == [
            "  a   b",
            "  aa  b",
            "  aaa b",
        ]

    def test__rendered_column_width_can_be_adjusted_without_indentation(
        self, settings: Settings, table_renderer: TableRenderer
    ) -> None:
        settings.indent = " " * 2
        settings.column_padding = " " * 1

        table_renderer.add_row("a", "b")
        table_renderer.add_row("aa", "b")
        table_renderer.add_row("aaa", "b")
        result = table_renderer.render(print_lines=False, indent=False)
        assert result == [
            "a   b",
            "aa  b",
            "aaa b",
        ]

    def test__coloring_should_not_affect_the_width_adjustment(
        self, settings: Settings, table_renderer: TableRenderer, mocker: MockerFixture
    ) -> None:
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 4
        settings.column_padding = " " * 2

        table_renderer.add_row("<<RED>>a<<RESET>>", "<<BLUE>>b<<RESET>>")
        table_renderer.add_row("<<RED>>aa<<RESET>>", "<<BLUE>>b<<RESET>>")
        table_renderer.add_row("<<RED>>aaa<<RESET>>", "<<BLUE>>b<<RESET>>")
        result = table_renderer.render(print_lines=False)

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
        self, settings: Settings, table_renderer: TableRenderer, mocker: MockerFixture
    ) -> None:
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 2
        settings.column_padding = " " * 1

        table_renderer.add_row(
            "<<BOLD>>[<<RED>>1<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>a<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        table_renderer.add_row(
            "<<BOLD>>[<<RED>>2<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        table_renderer.add_row(
            "<<BOLD>>[<<RED>>3<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aaa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        result = table_renderer.render(
            column_alignments=[
                table_renderer.ALIGN__LEFT,
                table_renderer.ALIGN__RIGHT,
                table_renderer.ALIGN__LEFT,
            ],
            indent=True,
            print_lines=False,
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
        self, settings: Settings, table_renderer: TableRenderer, mocker: MockerFixture
    ) -> None:
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 2
        settings.column_padding = " " * 1

        table_renderer.add_row(
            "<<BOLD>>[<<RED>>1<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>a<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        table_renderer.add_row(
            "<<BOLD>>[<<RED>>2<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        table_renderer.add_row(
            "<<BOLD>>[<<RED>>3<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aaa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        result = table_renderer.render(
            column_alignments=[
                table_renderer.ALIGN__LEFT,
                table_renderer.ALIGN__RIGHT,
                table_renderer.ALIGN__LEFT,
            ],
            indent=False,
            print_lines=False,
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
        self, settings: Settings, table_renderer: TableRenderer, mocker: MockerFixture
    ) -> None:
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 2
        settings.column_padding = " " * 1

        table_renderer.add_row(
            "<<BOLD>>[<<RED>>1<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>a<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        table_renderer.add_row(
            "<<BOLD>>[<<RED>>2<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        table_renderer.add_row(
            "<<BOLD>>[<<RED>>3<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aaa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        table_renderer.render(
            column_alignments=[
                table_renderer.ALIGN__LEFT,
                table_renderer.ALIGN__RIGHT,
                table_renderer.ALIGN__LEFT,
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
        self, settings: Settings, table_renderer: TableRenderer, mocker: MockerFixture
    ) -> None:
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 2
        settings.column_padding = " " * 1

        table_renderer.add_row(
            "<<BOLD>>[<<RED>>1<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>a<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        table_renderer.add_row(
            "<<BOLD>>[<<RED>>2<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        table_renderer.add_row(
            "<<BOLD>>[<<RED>>3<<RESET>><<BOLD>>]<<RESET>>",
            "<<YELLOW>>aaa<<RESET>>",
            "<<DIM>>b<<RESET>>",
        )
        table_renderer.render(
            column_alignments=[
                table_renderer.ALIGN__LEFT,
                table_renderer.ALIGN__RIGHT,
                table_renderer.ALIGN__LEFT,
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
