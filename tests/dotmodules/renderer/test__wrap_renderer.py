import pytest

from dotmodules.renderer import Colors, WrapRenderer
from dotmodules.settings import Settings


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def colors():
    return Colors()


class TestWrapRenderingCases:
    def test__wrapping_wont_happen_for_shorter_text(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "short text"
        expected = "short text"

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

    def test__wrapping_will_happen_on_longer_text(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "longer text"
        expected = "\n".join(
            [
                "longer",
                "text",
            ]
        )

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

    def test__wrapping_will_happen_on_longer_text_in_all_cases(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "a b c d e f g h"
        expected = "\n".join(
            [
                "a b c d e",
                "f g h",
            ]
        )

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

    def test__longer_word_than_wrap_limit_will_be_an_overhagning_word(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "extralongword"
        expected = "extralongword"

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

    def test__longer_text_than_wrap_limit_in_context(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "extralongword it should be left as is"
        expected = "\n".join(
            [
                "extralongword",
                "it should",
                "be left as",
                "is",
            ]
        )

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

    def test__indentation_will_be_kept(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "  short text"
        expected = "\n".join(
            [
                "  short",
                "text",
            ]
        )

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

    def test__indentation_longer_than_the_limit__full_indentation_will_be_kept(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "               short text"
        expected = "\n".join(
            [
                "               short",
                "text",
            ]
        )

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

    def test__indentation_will_be_kept_before_the_too_long_word(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = " extralongword"
        expected = " extralongword"

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

    def test__indentation_will_be_kept_before_the_too_long_word_even_if_it_is_long(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "              extralongword"
        expected = "              extralongword"

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

    def test__longer_text_than_wrap_limit_in_context_with_indentation(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = " extralongword it should be left as is"
        expected = "\n".join(
            [
                " extralongword",
                "it should",
                "be left as",
                "is",
            ]
        )

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

    def test__coloring_tags_will_be_ignored(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColoringTagCache._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #                      |----10----|
        dummy_string = "<<BOLD>>short text<<RESET>>"
        expected = "boldshort textreset"

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__arbitraty_number_of_coloring_tags_can_be_handled(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColoringTagCache._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        dummy_string = "<<BOLD>><<RED>><<DIM>><<UNDERLINE>>short text<<RESET>>"
        expected = "boldreddimunderlineshort textreset"

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RED"),
                mocker.call(tag="DIM"),
                mocker.call(tag="UNDERLINE"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__coloring_tag_will_be_ignored_on_multiline_input_too(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColoringTagCache._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        dummy_string = "<<BOLD>><<RED>>longer<<RESET>> <<BOLD>><<BLUE>>text<<RESET>>"
        expected = "\n".join(
            [
                "boldredlongerreset",
                "boldbluetextreset",
            ]
        )

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
                mocker.call(tag="BLUE"),
            ]
        )

    def test__coloring_wont_interfere_with_extra_long_words(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColoringTagCache._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "<<BOLD>>extralongword<<RESET>>"
        expected = "boldextralongwordreset"

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__coloring_wont_interfere_with_extra_long_words_in_context(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColoringTagCache._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = (
            "<<BOLD>>extralongword<<RESET>> it should be <<BOLD>>left<<RESET>> as is"
        )
        expected = "\n".join(
            [
                "boldextralongwordreset",
                "it should",
                "be boldleftreset as",
                "is",
            ]
        )

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__coloring_wont_interfere_with_indented_extra_long_words(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColoringTagCache._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = " <<BOLD>>extralongword<<RESET>>"
        expected = " boldextralongwordreset"

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__coloring_wont_interfere_with_indented_extra_long_words_in_context(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColoringTagCache._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = (
            " <<BOLD>>extralongword<<RESET>> it should be <<BOLD>>left<<RESET>> as is"
        )
        expected = "\n".join(
            [
                " boldextralongwordreset",
                "it should",
                "be boldleftreset as",
                "is",
            ]
        )

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__global_indentation_will_be_respected_1(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = "  "
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        # The wrap limit will be shortened by the indentation size. Without
        # indentation this input won't be wrapped.
        #              |----8---|
        dummy_string = "short text"
        expected = "\n".join(
            [
                "  short",
                "  text",
            ]
        )

        wrap_renderer.render(string=dummy_string)
        mock_print.assert_called_with(expected)
