import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.renderer import (
    HeaderRenderer,
    PromptRenderer,
    Renderer,
    TableRenderer,
    WrapRenderer,
)
from dotmodules.settings import Settings


@pytest.fixture
def settings() -> Settings:
    settings = Settings()
    settings.indent = " "
    settings.text_wrap_limit = 80
    return settings


@pytest.fixture
def renderer(settings: Settings) -> Renderer:
    return Renderer(settings=settings)


class TestTopLevelRendererCases:
    def test__sub_renderers_can_be_reached(self, renderer: Renderer) -> None:
        assert isinstance(renderer.table, TableRenderer)
        assert isinstance(renderer.prompt, PromptRenderer)
        assert isinstance(renderer.wrap, WrapRenderer)
        assert isinstance(renderer.header, HeaderRenderer)

    def test__new_line_renderer(
        self, renderer: Renderer, mocker: MockerFixture
    ) -> None:
        mock_print = mocker.patch("dotmodules.renderer.print")
        renderer.empty_line()
        mock_print.assert_called_with("")
