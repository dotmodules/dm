import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.renderer import Colors, HeaderRenderer
from dotmodules.settings import Settings


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def colors() -> Colors:
    return Colors()


@pytest.fixture
def header_renderer(settings: Settings, colors: Colors) -> HeaderRenderer:
    return HeaderRenderer(settings=settings, colors=colors)


class TestHeaderRenderingCases:
    def test__header_will_be_prepended_with_the_same_width(
        self, header_renderer: HeaderRenderer, mocker: MockerFixture
    ) -> None:
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        dummy_lines = [
            "line 1",
            "line 2",
        ]

        header_renderer.render(
            header="<<RED>>header<<RESET>>",
            lines=dummy_lines,
            header_width=6,  # same as the decolored header
            separator="  ",
        )

        mock_print.assert_has_calls(
            [
                mocker.call("redheaderreset  line 1"),
                # The additional lines shouldn't deal with coloring spacing so
                # the whitespace before it is less than the previous header line
                # by the 'red' and 'reset' word lengths.
                mocker.call("        line 2"),
            ]
        )
        assert mock_print.call_count == 2
        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__header_will_be_right_aligned_for_longer_width(
        self, header_renderer: HeaderRenderer, mocker: MockerFixture
    ) -> None:
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        dummy_lines = [
            "line 1",
            "line 2",
        ]

        header_renderer.render(
            header="<<RED>>header<<RESET>>",
            lines=dummy_lines,
            header_width=8,
            separator="  ",
        )

        mock_print.assert_has_calls(
            [
                mocker.call("  redheaderreset  line 1"),
                mocker.call("          line 2"),
            ]
        )
        assert mock_print.call_count == 2
        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
            ]
        )
