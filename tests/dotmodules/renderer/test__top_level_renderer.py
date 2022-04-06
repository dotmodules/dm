import pytest

from dotmodules.renderer import PromptRenderer, Renderer, RowRenderer
from dotmodules.settings import Settings


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def renderer(settings):
    return Renderer(settings=settings)


class TestTopLevelRendererCases:
    def test__sub_renderers_can_be_reached(self, renderer):
        assert isinstance(renderer.rows, RowRenderer)
        assert isinstance(renderer.prompt, PromptRenderer)
