import pytest

from dotmodules.renderer import Colors, WrapRenderer
from dotmodules.settings import Settings


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def colors():
    return Colors()


class TestWrapRenderingWithoutColoringCases:
    def test__empty_string_remains_empty(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        dummy_string = ""

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call(""),
            ]
        )
        assert mock_print.call_count == 1

    def test__wrapping_wont_happen_for_shorter_text(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "short text"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("short text"),
            ]
        )
        assert mock_print.call_count == 1

    def test__wrapping_will_happen_on_longer_text(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "longer text"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("longer"),
                mocker.call("text"),
            ]
        )
        assert mock_print.call_count == 2

    def test__wrapping_will_happen_on_longer_text_with_multiple_words(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "a b c d e f g h"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("a b c d e"),
                mocker.call("f g h"),
            ]
        )
        assert mock_print.call_count == 2

    def test__longer_word_than_wrap_limit_will_be_an_overhagning_word(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "extralongword"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("extralongword"),
            ]
        )
        assert mock_print.call_count == 1

    def test__longer_text_than_wrap_limit_in_context_will_overhang(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "extralongword it should be left as is"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("extralongword"),
                mocker.call("it should"),
                mocker.call("be left as"),
                mocker.call("is"),
            ]
        )
        assert mock_print.call_count == 4

    def test__indentation_will_be_kept(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "  short text"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("  short"),
                mocker.call("text"),
            ]
        )
        assert mock_print.call_count == 2

    def test__indentation_longer_than_the_limit__full_indentation_will_be_kept(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "               short text"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("               short"),
                mocker.call("text"),
            ]
        )
        assert mock_print.call_count == 2

    def test__indentation_will_be_kept_before_the_too_long_word(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = " extralongword"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call(" extralongword"),
            ]
        )
        assert mock_print.call_count == 1

    def test__indentation_will_be_kept_before_the_too_long_word_even_if_it_is_long(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = "              extralongword"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("              extralongword"),
            ]
        )
        assert mock_print.call_count == 1

    def test__longer_text_than_wrap_limit_in_context_with_indentation(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----10----|
        dummy_string = " extralongword it should be left as is"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call(" extralongword"),
                mocker.call("it should"),
                mocker.call("be left as"),
                mocker.call("is"),
            ]
        )
        assert mock_print.call_count == 4

    def test__multiple_input_lines__empty_lines(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        dummy_string = "\n" "\n" "\n"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call(""),
                mocker.call(""),
                mocker.call(""),
            ]
        )
        assert mock_print.call_count == 3

    def test__multiple_input_lines_can_be_handled(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 20
        settings.indent = ""
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        dummy_string = "\n".join(
            [
                #       |----------20--------|
                "This is a bit longer text that will be tested.",
                "",
                "It also has some empty lines.",
                "- it contains",
                "- multiple levels",
                "  - of indentations",
                "",
                "Longer lines should be wrapped as it is expected.",
            ]
        )

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("This is a bit longer"),
                mocker.call("text that will be"),
                mocker.call("tested."),
                mocker.call(""),
                mocker.call("It also has some"),
                mocker.call("empty lines."),
                mocker.call("- it contains"),
                mocker.call("- multiple levels"),
                mocker.call("  - of indentations"),
                mocker.call(""),
                mocker.call("Longer lines should"),
                mocker.call("be wrapped as it is"),
                mocker.call("expected."),
            ]
        )
        assert mock_print.call_count == 13


class TestWrapRenderingWithColoringTagsCases:
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

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("boldshort textreset"),
            ]
        )
        assert mock_print.call_count == 1

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

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("boldreddimunderlineshort textreset"),
            ]
        )
        assert mock_print.call_count == 1

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

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("boldredlongerreset"),
                mocker.call("boldbluetextreset"),
            ]
        )
        assert mock_print.call_count == 2

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

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("boldextralongwordreset"),
            ]
        )
        assert mock_print.call_count == 1

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

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("boldextralongwordreset"),
                mocker.call("it should"),
                mocker.call("be boldleftreset as"),
                mocker.call("is"),
            ]
        )
        assert mock_print.call_count == 4

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

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call(" boldextralongwordreset"),
            ]
        )
        assert mock_print.call_count == 1

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

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call(" boldextralongwordreset"),
                mocker.call("it should"),
                mocker.call("be boldleftreset as"),
                mocker.call("is"),
            ]
        )
        assert mock_print.call_count == 4

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )


class TestWrapRenderingGlobalIndentationCases:
    def test__global_indentation_will_be_respected_1(self, settings, colors, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        settings.text_wrap_limit = 10
        settings.indent = "  "
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        # The wrap limit will be shortened by the indentation size. Without
        # indentation this input won't be wrapped.
        #              |----8---|
        dummy_string = "short text"

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("  short"),
                mocker.call("  text"),
            ]
        )
        assert mock_print.call_count == 2

    def test__coloring_wont_interfere_with_extra_long_words_in_context(
        self, settings, colors, mocker
    ):
        mock_print = mocker.patch("dotmodules.renderer.print")
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColoringTagCache._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        settings.text_wrap_limit = 10
        settings.indent = "  "
        wrap_renderer = WrapRenderer(settings=settings, colors=colors)

        #              |----8---|
        dummy_string = (
            "<<BOLD>>extralongword<<RESET>> it should be <<BOLD>>left<<RESET>> as is"
        )

        wrap_renderer.render(string=dummy_string)

        mock_print.assert_has_calls(
            [
                mocker.call("  boldextralongwordreset"),
                mocker.call("  it"),
                mocker.call("  should"),
                mocker.call("  be boldleftreset"),
                mocker.call("  as is"),
            ]
        )
        assert mock_print.call_count == 5

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )
