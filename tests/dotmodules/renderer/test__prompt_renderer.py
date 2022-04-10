import pytest

from dotmodules.renderer import Colors, PromptRenderer
from dotmodules.settings import Settings


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def colors():
    return Colors()


class TestPromptRenderingCases:
    def test__space_and_indent_can_be_resolved(self, settings, colors):
        settings.indent = " " * 4
        prompt_renderer = PromptRenderer(settings=settings, colors=colors)
        dummy_prommpt_template = "<<SPACE>>hello<<INDENT>>"
        expected = " hello    "
        result = prompt_renderer.render(prompt_template=dummy_prommpt_template)
        assert result == expected

    def test__colors_can_be_resolved_too(self, settings, colors, mocker):
        mock_load_color_for_tag = mocker.patch(
            "dotmodules.renderer.ColoringTagCache._load_color_for_tag",
            wraps=lambda tag: tag.lower(),
        )

        settings.indent = " " * 4
        prompt_renderer = PromptRenderer(settings=settings, colors=colors)
        dummy_prommpt_template = "<<RED>>hello<<RESET>>"
        expected = "redhelloreset"
        result = prompt_renderer.render(prompt_template=dummy_prommpt_template)
        assert result == expected

        mock_load_color_for_tag.assert_has_calls(
            [
                mocker.call(tag="RED"),
                mocker.call(tag="RESET"),
            ]
        )
