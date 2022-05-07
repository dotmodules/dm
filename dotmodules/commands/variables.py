from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


class VariablesCommand(Command):
    @property
    def match_pattern(self) -> str:
        return self._settings.hotkey_variables

    @property
    def summary(self) -> List[str]:
        return [
            f"<<BOLD>>[<<GREEN>>{self._settings.hotkey_variables}<<RESET>><<BOLD>>]<<RESET>>",
            "This is the variables command.",
        ]

    def execute(
        self,
        settings: Settings,
        modules: Modules,
        abort_interpreter: Callable[[], None],
        renderer: Renderer,
        commands: List[Command],
        parameters: Optional[List[str]] = None,
    ) -> None:
        renderer.empty_line()

        header_width = max([len(name) for name in modules.variables.keys()]) + len(
            settings.column_padding
        )
        body_width = (
            settings.text_wrap_limit - header_width - len(settings.column_padding)
        )
        header_separator = " "

        for name, values in modules.variables.items():
            text = renderer.wrap.render(
                string=" ".join(values),
                wrap_limit=body_width,
                print_lines=False,
                indent=False,
            )
            renderer.header.render(
                header=f"<<BOLD>>{name}<<RESET>>",
                header_width=header_width,
                lines=text,
                separator=header_separator,
            )

        renderer.empty_line()
