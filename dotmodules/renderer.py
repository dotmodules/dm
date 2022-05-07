import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, cast

from dotmodules.settings import Settings
from dotmodules.shell_adapter import ShellAdapter


@dataclass
class ColorizeResult:
    colorized_string: str
    additional_width: int


class ColorAdapter:
    """
    Adapter class that is responsible to retrieve and cache the ANSI color
    escape sequences from the system.

    Under the hood it is using 'tput' to get the color codes. It has a
    predefined list of recognized tags in the 'TAG_MAPPING' class variable.
    Those predefined tags are mapped to valid tput parameters that will be fed
    to the external 'tput' command.

    These set of tags offers the basic colors and text decorations. To have the
    full range of the 8 bit color palette you can submit a color code in a
    numeric form.
    """

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

    def __init__(self) -> None:
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
        shell_result = ShellAdapter.execute_and_capture(command=command)
        if shell_result.status_code == 0:
            return shell_result.stdout[0]
        else:
            # We are ignoring the fact that the 'tput' call has failed and
            # returning an empty string.
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

    # Search pattern to capture the valid tag value discarding the starting and
    # closing angle brackets. It is also used to remove the coloring tags from
    # the string.
    tag_pattern = re.compile(r"<<([A-Z]+|[0-9]{1,3})(?=>>)>>")
    # Colorizing tag template which is used to replace the coloring tags in the
    # given string.
    tag_template = "<<{tag}>>"

    def __init__(self) -> None:
        self._color_adapter = ColorAdapter()

    def decolor_string(self, string: str) -> str:
        return re.sub(self.tag_pattern, "", string)

    def decolored_width(self, string: str) -> int:
        return len(self.decolor_string(string=string))

    def colorize(self, string: str) -> ColorizeResult:
        """
        Replaces the recognized coloring tags with the loaded coloring values.
        It will calculate the additional width the given string will gain
        compared to its decolored width due to the way the ANSI escape sequences
        work.
        """
        additional_width = 0

        # Iterating over the coloring tags in the sring and replacing them with
        # the ANSI escape sequences while keeping track of the additional width
        # gain.
        if tags := self._get_tag_list(string=string):
            for tag in tags:
                replaceable_tag = self.tag_template.format(tag=tag)
                coloring_sequence = self._color_adapter.resolve_tag(tag=tag)
                # Replacing only the first occurance.
                string = string.replace(replaceable_tag, coloring_sequence, 1)
                additional_width += len(coloring_sequence)

        return ColorizeResult(
            colorized_string=string, additional_width=additional_width
        )

    def _get_tag_list(self, string: str) -> Optional[Tuple[str]]:
        if matches := re.findall(self.tag_pattern, string):
            # Explicitly casting the resulted matches.
            return cast(Tuple[str], tuple(matches))
        else:
            return None


class RenderError(ValueError):
    pass


class TableRenderer:
    """
    Stateful table randerer that needs to be filled up with rows with the same
    column number.
    """

    # Alignment templates for the cells to be able to align them inside given
    # maximum cell width. Note that the tempaltes has to be prepared by
    # formatting them with the width first, then with the colored value.
    ALIGN__LEFT = "{{value:<{width}}}"
    ALIGN__CENTER = "{{value:^{width}}}"
    ALIGN__RIGHT = "{{value:>{width}}}"

    def __init__(self, settings: Settings, colors: Colors) -> None:
        self._settings = settings
        self._colors = colors
        self._row_buffer: List[List[str]] = []

    def add_row(self, *cell_values: str) -> None:
        """
        Adding a row to the row cache to render them later on into a uniform
        table.
        """
        row = [str(value).strip() for value in cell_values]
        self._row_buffer.append(row)

    def render(
        self,
        column_alignments: Optional[List[str]] = None,
        indent: bool = True,
        print_lines: bool = True,
    ) -> List[str]:
        """
        Rendering the registered rows, then freeing up the internal cache to be
        able to render a new table.

        During rendering the global column widths will be calculated. Then each
        cell in a row gets colorized and aligned inside the cell width, then the
        whole row will be indented if needed.
        """

        column_widths = self._calculate_max_column_width(buffer=self._row_buffer)

        # The default alignment is align left.
        if not column_alignments:
            column_alignments = [self.ALIGN__LEFT] * len(column_widths)

        output_lines = []

        for row in self._row_buffer:
            # Rendering each cell in a row by taking one cell at a time zipped
            # together for the max width and alignment for the given column.
            rendered_cells = [
                self._render_cell(
                    cell=item, width=width, alignment_template=alignment_template
                )
                for item, width, alignment_template in zip(
                    row, column_widths, column_alignments
                )
            ]

            # Joining together the cells with the predefined cell separator string.
            line = self._settings.column_padding.join(rendered_cells)

            # Indenting each row if needed.
            if indent:
                line = self._settings.indent + line

            output_lines.append(line)

        # Resetting the row buffer for the next table rendering.
        self._row_buffer = []

        if print_lines:
            for line in output_lines:
                print(line)

        return output_lines

    def _render_cell(self, cell: str, width: int, alignment_template: str) -> str:
        """
        Coloring the cell content while getting the additional width gain from
        the resolved ANSI coloring escape sequences. After coloring, we have the
        final width of the cell, so we can render the final alignment inside the
        cell width based on the given alignment template.
        """
        colorized_result = self._colors.colorize(string=cell)
        width += colorized_result.additional_width

        # Preparing the given alignment template with the final width.
        prepared_alignment_template = alignment_template.format(width=width)

        # Rendering the prepared alignment template with the colored cell value.
        return prepared_alignment_template.format(
            value=colorized_result.colorized_string
        )

    def _calculate_max_column_width(self, buffer: List[List[str]]) -> List[int]:
        """
        Returns the maximum width of the columns as a list of integers. Note
        that the width is calculated based on the decolorized size. This is
        important because the coloring tags has different size than the final
        ANSI escape sequences.
        """
        if len(set([len(row) for row in buffer])) != 1:
            raise RenderError(f"inconsistent column count in buffer: '{buffer}'")

        column_widths = [
            [self._colors.decolored_width(string=item) for item in row]
            for row in buffer
        ]
        # Zips together the rows by index = getting all the items in a column.
        return [max(columns) for columns in zip(*column_widths)]


class PromptRenderer:
    """
    Specialized renderer that simply renders the provided prompt template.
    Besides the coloring tags it can recognize the <<SPACE>> and <<INDENT>> tags
    too.
    """

    def __init__(self, settings: Settings, colors: Colors) -> None:
        self._colors = colors
        self._settings = settings

    def render(self, prompt_template: str) -> str:
        prompt = prompt_template.replace("<<SPACE>>", " ")
        prompt = prompt.replace("<<INDENT>>", self._settings.indent)
        colorize_result = self._colors.colorize(string=prompt)
        return colorize_result.colorized_string


class WrapRenderer:
    """
    Generic renderer that wraps arbitrary text into the global wrap limit by
    respecting the global indentation.

    It has the following rules:

    1. A word is considered an overhanging word if any of the word's character
       touching the glogal wrapping limit.
    2. Overhanging words won't be splitted.
    3. Overhanging words will be wrapped to the next line if they have a clear
       wrapping point before them.
    4. A clear wrapping point is a whitespace that separates the overhanging
       word from a previous word.
    5. If there is no clear wrapping point i.e. the overhanging word is the only
       word in the line the overhanging word won't be wrapped
    6. Whitespace before leading words in the lines are considered indentation
       wich is an intended formatting hence they will be kept.
    7. Trailing whitespace will be trimmed.
    8. All of the previous operations will respect the global indentation if the
       indentation mode is active.
    """

    def __init__(self, settings: Settings, colors: Colors) -> None:
        self._colors = colors
        self._settings = settings

    def render(
        self,
        string: str,
        indent: bool = True,
        wrap_limit: Optional[int] = None,
        print_lines: bool = True,
    ) -> List[str]:
        # Defaulting to the global text wrapping and indenting values if needed.
        if wrap_limit is None:
            wrap_limit = self._settings.text_wrap_limit
        if indent:
            wrap_limit -= len(self._settings.indent)

        lines = string.splitlines()
        output_lines = []

        if not lines:
            # If an empty string is provided an empty line will be returned.
            output_lines.append("")
        else:
            for line in lines:
                # Wrapping each input line into possible multiple lines.
                wrapped_lines = self._render_line(line=line, wrap_limit=wrap_limit)
                # Indenting the wrapped lines if needed.
                if indent:
                    wrapped_lines = [
                        self._settings.indent + wrapped_line
                        for wrapped_line in wrapped_lines
                    ]
                output_lines += wrapped_lines

        if print_lines:
            for line in output_lines:
                print(line)

        return output_lines

    def _render_line(self, line: str, wrap_limit: int) -> List[str]:
        """
        Processing the input line with a two-state state machine.

        [*] --> APPEND
        APPEND -[whitespace]-> APPEND : appending character to line buffer
        APPEND -[non-whitecpace]-> BUFFER : entering word buffering saving
        APPEND -[non-whitecpace]-> APPEND : appending to word buffer
        BUFFER -[whitespace]-> APPEND : processing word buffer, updating or
                                        finalizing line buffer

        During word buffer processing the buffer will be colored and wrapped if
        needed in the next line. Wrapping is calculated based on the decolored
        with of the words.

        After each character is processed in the line and there are content in
        the word or line buffers, it will be processed too.
        """
        wrap_count = 0
        word_buffer = ""
        line_buffer = ""

        wrapped_lines = []

        for char in line:
            if not word_buffer:
                # STATE APPEND - If the word buffer is empty we are in the
                # appeding state when each whitespace character will be appended
                # to the line buffer.
                if char.isspace():
                    line_buffer += char
                    wrap_count += 1
                else:
                    word_buffer += char
            else:
                # STATE BUFFER - If the word buffer is started filling we are
                # collecting the incomming non-whitespace charecters into it. If
                # a new whatespace character arrives, the word buffer will be
                # colored, and the decision will be made if it can be appended
                # to the current line buffer, or a new line should be started
                # with the current word buffer wrapped into it.
                if not char.isspace():
                    word_buffer += char
                else:
                    word_length = self._colors.decolored_width(string=word_buffer)
                    colorize_result = self._colors.colorize(string=word_buffer)
                    colorized_word = colorize_result.colorized_string
                    word_buffer = ""

                    if (wrap_count + word_length) > wrap_limit:
                        if wrap_count > 0:
                            if line_buffer.isspace():
                                # Leading whitespace will be considered as
                                # indentation.
                                line_buffer += colorized_word
                                wrapped_lines.append(line_buffer)
                                # Resetting the additional state as this step
                                # was a slight hack.
                                colorized_word = ""
                                word_length = 0
                                char = ""
                            else:
                                wrapped_lines.append(line_buffer)
                        line_buffer = ""
                        wrap_count = 0

                    # Adding the colorized word and the current whitespace
                    # character to the line buffer and logging the widths.
                    line_buffer += colorized_word + char
                    wrap_count += word_length + 1

        # POST PROCESSING THE WORD AND LINE BUFFERS Process the left over
        # content of the word buffer.
        if word_buffer:
            word_length = self._colors.decolored_width(string=word_buffer)
            colorize_result = self._colors.colorize(string=word_buffer)
            colorized_word = colorize_result.colorized_string
        else:
            word_length = 0
            colorized_word = ""

        # Append it to the line or append it to a new line after the leftover
        # line gets appended.
        if (wrap_count + word_length) > wrap_limit:
            if wrap_count > 0:
                if line_buffer.isspace():
                    line_buffer += colorized_word
                    wrapped_lines.append(line_buffer)
                else:
                    wrapped_lines.append(line_buffer)
                    wrapped_lines.append(colorized_word)
            else:
                wrapped_lines.append(colorized_word)
        else:
            line_buffer += colorized_word
            wrapped_lines.append(line_buffer)

        # Trailing whitespace will be trimmed.
        return [line.rstrip() for line in wrapped_lines]


class HeaderRenderer:
    """
    Finalizer renderer that will print a header section before the lines passed
    to it.
    """

    def __init__(self, settings: Settings, colors: Colors) -> None:
        self._colors = colors
        self._settings = settings

    def render(
        self, header: str, lines: List[str], header_width: int, separator: str
    ) -> None:
        colorize_result = self._colors.colorize(string=header)
        colorized_header = colorize_result.colorized_string
        colorized_width = header_width + colorize_result.additional_width

        prepared_alignment = "{{value:>{width}}}{separator}".format(
            width=colorized_width,
            separator=separator,
        )
        finalized_header = prepared_alignment.format(value=colorized_header)

        header_added = False
        for line in lines:
            if header_added:
                print(" " * header_width + separator + line)
            else:
                header_added = True
                print(finalized_header + line)


class Renderer:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._colors = Colors()
        self._table_renderer = TableRenderer(settings=settings, colors=self._colors)
        self._prompt_renderer = PromptRenderer(settings=settings, colors=self._colors)
        self._wrap_renderer = WrapRenderer(settings=settings, colors=self._colors)
        self._header_renderer = HeaderRenderer(settings=settings, colors=self._colors)

    def empty_line(self) -> None:
        print("")

    @property
    def table(self) -> TableRenderer:
        return self._table_renderer

    @property
    def prompt(self) -> PromptRenderer:
        return self._prompt_renderer

    @property
    def wrap(self) -> WrapRenderer:
        return self._wrap_renderer

    @property
    def header(self) -> HeaderRenderer:
        return self._header_renderer
