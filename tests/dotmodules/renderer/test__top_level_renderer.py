import pytest

from dotmodules.renderer import PromptRenderer, Renderer, TableRenderer, WrapRenderer
from dotmodules.settings import Settings


@pytest.fixture
def settings():
    settings = Settings()
    settings.indent = " "
    settings.text_wrap_limit = 80
    return settings


@pytest.fixture
def renderer(settings):
    return Renderer(settings=settings)


class TestTopLevelRendererCases:
    def test__sub_renderers_can_be_reached(self, renderer):
        assert isinstance(renderer.table, TableRenderer)
        assert isinstance(renderer.prompt, PromptRenderer)
        assert isinstance(renderer.wrap, WrapRenderer)

    def test__new_line_renderer(self, renderer, mocker):
        mock_print = mocker.patch("dotmodules.renderer.print")
        renderer.empty_line()
        mock_print.assert_called_with("")
