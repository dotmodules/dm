import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, cast

from dotmodules.settings import Settings
from dotmodules.shell_adapter import ShellAdapter


@dataclass
class ColorizeResult:
    colorized_string: str
    additional_width: int


class ColoringTagCache:
    TAG_MAPPING = {
        "RED": "setaf 1",
        "GREEN": "setaf 2",
        "YELLOW": "setaf 3",
        "BLUE": "setaf 4",
        "MAGENTA": "setaf 5",
        "CYAN": "setaf 6",
        "RESET": "sgr0",
        "BOLD": "bold",
        "UNDERLINE": "smul",
        "HIGHLIGHT": "smso",
        "DIM": "dim",
    }

    NUMERIC_TAG_MAPPING = "setaf {tag}"

    COLOR_ADAPTER_SCRIPT_PATH = "utils/color_adapter.sh"

    def __init__(self):
        self._cache: Dict[str, str] = {}

    def resolve_tag(self, tag: str) -> str:
        if tag not in self._cache:
            self._cache[tag] = self._load_color_for_tag(tag=tag)
        return self._cache[tag]

    def _assemble_color_loading_command(self, tag: str) -> List[str]:
        command = [self.COLOR_ADAPTER_SCRIPT_PATH]
        if mapped_tag := self.TAG_MAPPING.get(tag):
            command += mapped_tag.split()
        else:
            if tag.isdigit():
                # Numeric tags will be loaded as color codes.
                command += self.NUMERIC_TAG_MAPPING.format(tag=tag).split()
            else:
                raise ValueError(f"unmapped tag has to be numeric: '{tag}'")
        return command

    def _load_color_for_tag(self, tag: str) -> str:
        command = self._assemble_color_loading_command(tag=tag)
        shell_result = ShellAdapter.execute(command=command)
        if shell_result.status_code == 0:
            return shell_result.stdout[0]
        else:
            # TODO: Warning should be raised here
            return ""


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

    def __init__(self):
        self._coloring_tag_cache = ColoringTagCache()

    def clean(self, string: str) -> str:
        return re.sub(self.tag_pattern, "", string)

    def real_width(self, string: str) -> int:
        return len(self.clean(string=string))

    def colorize(self, string: str) -> ColorizeResult:
        """
        Replaces the recognized coloring tags with the loaded coloring values.
        """
        additional_width = 0
        if tags := self._get_tag_list(string=string):
            for tag in tags:
                # We have to recreate the tag from the captured tag value, to be
                # able to replace it. During the processing we only care about
                # the tag value, the double angle brackets will be ignored,
                # hence the usage of the 'tag_template'.
                replaceable_tag = self.tag_template.format(tag=tag)
                tag_value = self._coloring_tag_cache.resolve_tag(tag=tag)
                string = string.replace(replaceable_tag, tag_value, 1)
                additional_width += len(tag_value)
        return ColorizeResult(
            colorized_string=string, additional_width=additional_width
        )

    def _get_tag_list(self, string: str) -> Optional[Tuple[str]]:
        if matches := re.findall(self.tag_pattern, string):
            return cast(Tuple[str], tuple(matches))
        else:
            return None


class RenderError(ValueError):
    pass


class RowRenderer:
    ALIGN__LEFT = "{{value:<{width}}}"
    ALIGN__CENTER = "{{value:^{width}}}"
    ALIGN__RIGHT = "{{value:>{width}}}"

    def __init__(self, settings: Settings, colors: Colors):
        self._settings = settings
        self._colors = colors
        self._row_buffer: List[List[str]] = []

    def add_row(self, *values: str):
        row = [str(value).strip() for value in values]
        self._row_buffer.append(row)

    def render_rows(self, column_alignments: Optional[List[str]] = None):
        column_widths = self._calculate_max_column_width(buffer=self._row_buffer)

        if not column_alignments:
            column_alignments = [self.ALIGN__LEFT] * len(column_widths)

        for row in self._row_buffer:
            rendered_columns = [
                self._render_item(
                    item=item, width=width, alignment_template=alignment_template
                )
                for item, width, alignment_template in zip(
                    row, column_widths, column_alignments
                )
            ]
            print(
                self._settings.indent
                + self._settings.column_padding.join(rendered_columns)
            )

        self._row_buffer = []

    def _render_item(self, item: str, width: int, alignment_template: str) -> str:
        colorized_result = self._colors.colorize(string=item)
        width += colorized_result.additional_width
        rendered_alignment_template = alignment_template.format(width=width)
        return rendered_alignment_template.format(
            value=colorized_result.colorized_string
        )

    def _calculate_max_column_width(self, buffer: List[List[str]]) -> List[int]:
        if len(set([len(row) for row in buffer])) != 1:
            raise RenderError("inconsistent column count")

        column_widths = [
            [self._colors.real_width(string=item) for item in row] for row in buffer
        ]
        return [max(columns) for columns in zip(*column_widths)]


class PromptRenderer:
    def __init__(self, settings: Settings, colors: Colors):
        self._colors = colors
        self._indent = settings.indent

    def render(self, prompt_template: str) -> str:
        prompt = prompt_template.replace("<<SPACE>>", " ").replace(
            "<<INDENT>>", self._indent
        )
        colorize_result = self._colors.colorize(string=prompt)
        return colorize_result.colorized_string


class WrapRenderer:
    def __init__(self, settings: Settings, colors: Colors):
        self._colors = colors
        self._wrap_limit = settings.text_wrap_limit - len(settings.indent)
        self._indent = settings.indent

    def render(self, string: str):
        lines = string.splitlines()
        if not lines:
            return print("")
        for line in lines:
            wrapped_lines = self._render_line(line=line)
            for wrapped_line in wrapped_lines:
                print(self._indent + wrapped_line)

    def _render_line(self, line: str) -> List[str]:
        wrap_count = 0
        word_buffer = ""
        line_buffer = ""
        wrapped_lines = []
        for char in line:
            if not word_buffer:
                if char.isspace():
                    line_buffer += char
                    wrap_count += 1
                else:
                    word_buffer += char
            else:
                if char.isspace():
                    word_length = self._colors.real_width(string=word_buffer)
                    colorize_result = self._colors.colorize(string=word_buffer)
                    colorized_word = colorize_result.colorized_string
                    word_buffer = ""

                    if (wrap_count + word_length) > self._wrap_limit:
                        if wrap_count > 0:
                            if line_buffer.isspace():
                                # If there is only whitespace present in the
                                # line, it should be considered as an
                                # indentaion, and we should add it right before
                                # the long word.
                                line_buffer += colorized_word
                                wrapped_lines.append(line_buffer.rstrip())
                                # Resetting the additional state as this step
                                # was a slight hack.
                                colorized_word = ""
                                word_length = 0
                                char = ""
                            else:
                                wrapped_lines.append(line_buffer.rstrip())
                        line_buffer = ""
                        wrap_count = 0

                    line_buffer += colorized_word + char
                    wrap_count += word_length + 1
                else:
                    word_buffer += char

        # Process the left over content of the word buffer.
        if word_buffer:
            word_length = self._colors.real_width(string=word_buffer)
            colorize_result = self._colors.colorize(string=word_buffer)
            colorized_word = colorize_result.colorized_string
        else:
            word_length = 0
            colorized_word = ""

        # Append it to the line or append it to a new line after the leftover
        # line gets appended.
        if (wrap_count + word_length) > self._wrap_limit:
            if wrap_count > 0:
                if line_buffer.isspace():
                    line_buffer += colorized_word
                    wrapped_lines.append(line_buffer.rstrip())
                else:
                    wrapped_lines.append(line_buffer.rstrip())
                    wrapped_lines.append(colorized_word)
            else:
                wrapped_lines.append(colorized_word)
        else:
            line_buffer += colorized_word
            wrapped_lines.append(line_buffer.rstrip())

        return wrapped_lines


class Renderer:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._colors = Colors()
        self._row_renderer = RowRenderer(settings=settings, colors=self._colors)
        self._prompt_renderer = PromptRenderer(settings=settings, colors=self._colors)
        self._wrap_renderer = WrapRenderer(settings=settings, colors=self._colors)

    def empty_line(self):
        print("")

    @property
    def rows(self):
        return self._row_renderer

    @property
    def prompt(self):
        return self._prompt_renderer

    @property
    def wrap(self):
        return self._wrap_renderer
