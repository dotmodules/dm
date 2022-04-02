import pytest

from dotmodules.renderer import Renderer, RenderError, RenderItem
from dotmodules.settings import Settings


@pytest.fixture
def settings():
    return Settings()


class TestRenderItemCases:
    def test__real_length_can_be_calculated(self):
        dummy_value = "a" * 12
        dummy_style = "style"
        render_item = RenderItem(value=dummy_value, style=dummy_style)

        assert render_item.width == 12

    def test__real_length_can_be_calculated__value_will_be_stripped(self):
        dummy_value = "    " + "a" * 12 + "  "
        dummy_style = "style"
        render_item = RenderItem(value=dummy_value, style=dummy_style)

        assert render_item.width == 12

    def test__item_can_be_rendered__left_align(self):
        dummy_value = "hello"
        dummy_style = "[{{value:{width}}}]"
        render_item = RenderItem(value=dummy_value, style=dummy_style)

        assert render_item.render(width=6) == "[hello ]"

    def test__item_can_be_rendered__right_align(self):
        dummy_value = "hello"
        dummy_style = "[{{value:>{width}}}]"
        render_item = RenderItem(value=dummy_value, style=dummy_style)

        assert render_item.render(width=6) == "[ hello]"

    def test__item_can_be_rendered__centered(self):
        dummy_value = "hello"
        dummy_style = "[{{value:^{width}}}]"
        render_item = RenderItem(value=dummy_value, style=dummy_style)

        assert render_item.render(width=7) == "[ hello ]"

    def test__item_can_be_rendered__whitespace_gets_ignored(self):
        dummy_value = "      hello    "
        dummy_style = "[{{value:^{width}}}]"
        render_item = RenderItem(value=dummy_value, style=dummy_style)

        assert render_item.render(width=7) == "[ hello ]"


class TestRowRenderingCases:
    def test__column_width_can_be_calculated(self, settings, mocker):
        dummy_buffer = [
            [
                RenderItem(value="aaa", style=""),
                RenderItem(value="a", style=""),
                RenderItem(value="a", style=""),
            ],
            [
                RenderItem(value="a", style=""),
                RenderItem(value="aaa", style=""),
                RenderItem(value="a", style=""),
            ],
            [
                RenderItem(value="a", style=""),
                RenderItem(value="a", style=""),
                RenderItem(value="aaa", style=""),
            ],
        ]
        result = Renderer._calculate_max_column_width(buffer=dummy_buffer)
        assert result == [3, 3, 3]

    def test__inconsistent_columns__error(self, settings, mocker):
        dummy_buffer = [
            [
                RenderItem(value="a", style=""),
                RenderItem(value="a", style=""),
            ],
            [
                RenderItem(value="a", style=""),
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
            styles=[
                renderer.STYLE__DEFAULT__LEFT,
                renderer.STYLE__DEFAULT__LEFT,
            ],
        )
        renderer.add_row(
            values=[
                "aa",
                "b",
            ],
            styles=[
                renderer.STYLE__DEFAULT__LEFT,
                renderer.STYLE__DEFAULT__LEFT,
            ],
        )
        renderer.add_row(
            values=[
                "aaa",
                "b",
            ],
            styles=[
                renderer.STYLE__DEFAULT__LEFT,
                renderer.STYLE__DEFAULT__LEFT,
            ],
        )
        renderer.commit_rows()
        expected_calls = [
            mocker.call("    a    b"),
            mocker.call("    aa   b"),
            mocker.call("    aaa  b"),
        ]
        mock_print.assert_has_calls(expected_calls)
