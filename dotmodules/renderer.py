from dataclasses import dataclass
from typing import List

from dotmodules.settings import Settings


@dataclass
class RenderItem:
    value: str
    style: str

    @property
    def width(self) -> int:
        return len(self.value.strip())

    def render(self, width: int) -> str:
        rendered_style = self.style.format(width=width)
        return rendered_style.format(value=str(self.value.strip()))


class RenderError(ValueError):
    pass


class Renderer:
    STYLE__DEFAULT__LEFT = "{{value:<{width}}}"
    STYLE__DEFAULT__CENTER = "{{value:^{width}}}"
    STYLE__DEFAULT__RIGHT = "{{value:>{width}}}"
    STYLE__BOLD = "<b>{value}</b>"

    def __init__(self, settings: Settings):
        self._settings = settings
        self._row_buffer: List[List[RenderItem]] = []

    def add_row(self, values: List[str], styles: List[str]):
        row = [
            RenderItem(value=value, style=style) for style, value in zip(styles, values)
        ]
        self._row_buffer.append(row)

    @staticmethod
    def _calculate_max_column_width(buffer: List[List[RenderItem]]) -> List[int]:
        if len(set([len(row) for row in buffer])) != 1:
            raise RenderError("inconsistent column count")

        column_widths = [[item.width for item in row] for row in buffer]
        return [max(columns) for columns in zip(*column_widths)]

    def commit_rows(self):
        column_widths = self._calculate_max_column_width(buffer=self._row_buffer)

        for row in self._row_buffer:
            rendered_columns = [
                item.render(width=width) for item, width in zip(row, column_widths)
            ]
            print(
                self._settings.indent
                + self._settings.column_padding.join(rendered_columns)
            )

        self._row_buffer = []
