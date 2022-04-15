import pytest

from dotmodules.renderer import Colors, WrapRenderer
from dotmodules.settings import Settings


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def colors():
    return Colors()


@pytest.fixture
def wrap_renderer(settings, colors):
    return WrapRenderer(settings=settings, colors=colors)


class TestWrapRenderingWithoutColoringCases:
    def test__empty_string_remains_empty(self, wrap_renderer):
        dummy_string = ""

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "",
        ]

    def test__wrapping_wont_happen_for_shorter_text(self, wrap_renderer):
        #              |----10----|
        dummy_string = "short text"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "short text",
        ]

    def test__wrapping_will_happen_on_longer_text(self, wrap_renderer):
        #              |----10----|
        dummy_string = "longer text"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "longer",
            "text",
        ]

    def test__wrapping_will_happen_on_longer_text_with_multiple_words(
        self, wrap_renderer
    ):
        #              |----10----|
        dummy_string = "a b c d e f g h"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "a b c d e",
            "f g h",
        ]

    def test__longer_word_than_wrap_limit_will_be_an_overhagning_word(
        self, wrap_renderer
    ):
        #              |----10----|
        dummy_string = "extralongword"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "extralongword",
        ]

    def test__longer_text_than_wrap_limit_in_context_will_overhang(self, wrap_renderer):
        #              |----10----|
        dummy_string = "extralongword it should be left as is"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "extralongword",
            "it should",
            "be left as",
            "is",
        ]

    def test__indentation_will_be_kept(self, wrap_renderer):
        #              |----10----|
        dummy_string = "  short text"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "  short",
            "text",
        ]

    def test__indentation_longer_than_the_limit__full_indentation_will_be_kept(
        self, wrap_renderer
    ):
        #              |----10----|
        dummy_string = "               short text"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "               short",
            "text",
        ]

    def test__indentation_will_be_kept_before_the_too_long_word(self, wrap_renderer):
        #              |----10----|
        dummy_string = " extralongword"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            " extralongword",
        ]

    def test__indentation_will_be_kept_before_the_too_long_word_even_if_it_is_long(
        self, wrap_renderer
    ):
        #              |----10----|
        dummy_string = "              extralongword"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "              extralongword",
        ]

    def test__longer_text_than_wrap_limit_in_context_with_indentation(
        self, wrap_renderer
    ):
        #              |----10----|
        dummy_string = " extralongword it should be left as is"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            " extralongword",
            "it should",
            "be left as",
            "is",
        ]

    def test__multiple_input_lines__empty_lines(self, wrap_renderer):
        dummy_string = "\n\n\n"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "",
            "",
            "",
        ]

    def test__multiple_input_lines_can_be_handled(self, wrap_renderer):
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

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=20, return_lines=True
        )

        assert result == [
            "This is a bit longer",
            "text that will be",
            "tested.",
            "",
            "It also has some",
            "empty lines.",
            "- it contains",
            "- multiple levels",
            "  - of indentations",
            "",
            "Longer lines should",
            "be wrapped as it is",
            "expected.",
        ]


class TestWrapRenderingPrinOutputCases:
    def test__multiple_input_lines_can_be_handled(self, wrap_renderer, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")

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

        wrap_renderer.render(string=dummy_string, indent=False, wrap_limit=20)

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
    def test__coloring_tags_will_be_ignored(self, wrap_renderer, mocker):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        #                      |----10----|
        dummy_string = "<<BOLD>>short text<<RESET>>"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "boldshort textreset",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__arbitraty_number_of_coloring_tags_can_be_handled(
        self, wrap_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        dummy_string = "<<BOLD>><<RED>><<DIM>><<UNDERLINE>>short text<<RESET>>"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "boldreddimunderlineshort textreset",
        ]

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
        self, wrap_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        dummy_string = "<<BOLD>><<RED>>longer<<RESET>> <<BOLD>><<BLUE>>text<<RESET>>"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "boldredlongerreset",
            "boldbluetextreset",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
                mocker.call(tag="BLUE"),
            ]
        )

    def test__coloring_wont_interfere_with_extra_long_words(
        self, wrap_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        #              |----10----|
        dummy_string = "<<BOLD>>extralongword<<RESET>>"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "boldextralongwordreset",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__coloring_wont_interfere_with_extra_long_words_in_context(
        self, wrap_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        #              |----10----|
        dummy_string = (
            "<<BOLD>>extralongword<<RESET>> it should be <<BOLD>>left<<RESET>> as is"
        )

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            "boldextralongwordreset",
            "it should",
            "be boldleftreset as",
            "is",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__coloring_wont_interfere_with_indented_extra_long_words(
        self, wrap_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        #              |----10----|
        dummy_string = " <<BOLD>>extralongword<<RESET>>"

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            " boldextralongwordreset",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__coloring_wont_interfere_with_indented_extra_long_words_in_context(
        self, wrap_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        #              |----10----|
        dummy_string = (
            " <<BOLD>>extralongword<<RESET>> it should be <<BOLD>>left<<RESET>> as is"
        )

        result = wrap_renderer.render(
            string=dummy_string, indent=False, wrap_limit=10, return_lines=True
        )

        assert result == [
            " boldextralongwordreset",
            "it should",
            "be boldleftreset as",
            "is",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )


class TestWrapRenderingGlobalIndentationCases:
    def test__global_indentation_will_be_respected_with_global_width(
        self, settings, wrap_renderer, mocker
    ):
        settings.text_wrap_limit = 10
        settings.indent = "  "

        # The wrap limit will be shortened by the indentation size. Without
        # indentation this input won't be wrapped.
        #              |----8---|
        dummy_string = "short text"

        result = wrap_renderer.render(string=dummy_string, return_lines=True)

        assert result == [
            "  short",
            "  text",
        ]

    def test__global_indentation_will_be_respected_with_defined_width(
        self, settings, wrap_renderer
    ):
        settings.indent = "  "

        # The wrap limit will be shortened by the indentation size. Without
        # indentation this input won't be wrapped.
        #              |----8---|
        dummy_string = "short text"

        result = wrap_renderer.render(
            string=dummy_string, wrap_limit=10, return_lines=True
        )

        assert result == [
            "  short",
            "  text",
        ]

    def test__global_indentation_will_be_respected_while_colored_with_global_width(
        self, settings, wrap_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        settings.text_wrap_limit = 10
        settings.indent = "  "

        #              |----8---|
        dummy_string = (
            "<<BOLD>>extralongword<<RESET>> it should be <<BOLD>>left<<RESET>> as is"
        )

        result = wrap_renderer.render(string=dummy_string, return_lines=True)

        assert result == [
            "  boldextralongwordreset",
            "  it",
            "  should",
            "  be boldleftreset",
            "  as is",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )

    def test__global_indentation_will_be_respected_while_colored_with_defined_width(
        self, settings, wrap_renderer, mocker
    ):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColorAdapter._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )
        settings.indent = "  "

        #              |----8---|
        dummy_string = (
            "<<BOLD>>extralongword<<RESET>> it should be <<BOLD>>left<<RESET>> as is"
        )

        result = wrap_renderer.render(
            string=dummy_string, wrap_limit=10, return_lines=True
        )

        assert result == [
            "  boldextralongwordreset",
            "  it",
            "  should",
            "  be boldleftreset",
            "  as is",
        ]

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="BOLD"),
                mocker.call(tag="RESET"),
            ]
        )
