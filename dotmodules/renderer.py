import re
from typing import Dict, List, Optional, Tuple, cast

from dotmodules.settings import Settings
from dotmodules.shell_adapter import ShellAdapter


class Colors:
    """
    Color handling class that is loading the color control codes from an
    external tput based shell script on demand while caching the results.

    Color tags has a very strict syntax: <<TAG>>

    Opening and closing double angle brackets enclosing the tag name that should
    be an UPPERCASE word or a pure numeric value. For the uppercase words there
    is a lookup table that will contain all the accepted tags (see the
    'tag_mapping' class variable). The numeric tags will be resolved as pure
    color codes.
    """

    tag_pattern = re.compile(r"<<([A-Z]+|[0-9]{1,3})(?=>>)>>")
    tag_template = "<<{tag}>>"
    color_cache: Dict[str, str] = {}

    tag_mapping = {
        "RED": "setaf 1",
        "GREEN": "setaf 2",
        "YELLOW": "setaf 3",
        "BLUE": "setaf 4",
        "MAGENTA": "setaf 5",
        "CYAN": "setaf 6",
        "RESET": "sgr0",
        "BOLD": "bold",
    }

    numeric_tag_mapping = "setaf {tag}"

    command = ["utils/color_adapter.sh"]

    @classmethod
    def clean(cls, string: str) -> str:
        return re.sub(cls.tag_pattern, "", string)

    @classmethod
    def colorize(cls, string: str) -> str:
        if tags := cls._get_tag_list(string=string):
            cls._update_color_cache(tags=tags)
            for tag in tags:
                string = string.replace(
                    cls.tag_template.format(tag=tag), cls.color_cache[tag], 1
                )
        return string

    @classmethod
    def _get_tag_list(cls, string: str) -> Optional[Tuple[str]]:
        if matches := re.findall(cls.tag_pattern, string):
            return cast(Tuple[str], tuple(matches))
        else:
            return None

    @classmethod
    def _assemble_color_loading_command(cls, tag: str) -> List[str]:
        command = cls.command
        if mapped_tag := cls.tag_mapping.get(tag):
            command += mapped_tag.split()
        else:
            if tag.isdigit():
                # Numeric tags will be loaded as color codes.
                command += cls.numeric_tag_mapping.format(tag=tag).split()
            else:
                raise ValueError(f"unmapped tag has to be numeric: '{tag}'")
        return command

    @classmethod
    def _load_color_for_tag(cls, tag: str) -> str:
        command = cls._assemble_color_loading_command(tag=tag)
        shell_result = ShellAdapter.execute(command=command)
        if shell_result.status_code == 0:
            return shell_result.stdout[0]
        else:
            # TODO: Warning should be raised here
            return ""

    @classmethod
    def _update_color_cache(cls, tags: Tuple[str]) -> None:
        for tag in tags:
            if tag not in cls.color_cache:
                cls.color_cache[tag] = cls._load_color_for_tag(tag=tag)


class RowItem:
    ALIGN__LEFT = "{{value:<{width}}}"
    ALIGN__CENTER = "{{value:^{width}}}"
    ALIGN__RIGHT = "{{value:>{width}}}"

    def __init__(
        self,
        value: str,
        alignment: Optional[str] = None,
    ):
        if not alignment:
            alignment = self.ALIGN__LEFT

        self._value = str(value).strip()
        self._alignment = alignment

    @property
    def width(self) -> int:
        return len(Colors.clean(string=self._value))

    def render(self, width: int) -> str:
        colored = Colors.colorize(string=self._value)
        rendered_alignment = self._alignment.format(width=width)
        return rendered_alignment.format(value=colored)


class RenderError(ValueError):
    pass


class Renderer:
    # Proxy class variable to be able to reach the styles from the a renderer
    # object.
    row = RowItem

    def __init__(self, settings: Settings):
        self._settings = settings
        self._row_buffer: List[List[RowItem]] = []

    def add_row(self, values: List[str], alignments: List[str]):
        row = [
            RowItem(value=value, alignment=alignment)
            for value, alignment in zip(values, alignments)
        ]
        self._row_buffer.append(row)

    @staticmethod
    def _calculate_max_column_width(buffer: List[List[RowItem]]) -> List[int]:
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
