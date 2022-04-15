from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


class HelpCommand(Command):
    @property
    def match_pattern(self):
        return self._settings.hotkey_help

    @property
    def summary(self) -> List[str]:
        return [
            f"<<BOLD>>[<<BLUE>>{self._settings.hotkey_help}<<RESET>><<BOLD>>]<<RESET>>",
            "Prints out this help message.",
        ]

    @property
    def is_default(self) -> bool:
        return True

    def execute(
        self,
        settings: Settings,
        modules: Modules,
        abort_interpreter: Callable,
        renderer: Renderer,
        commands: List[Command],
        parameters: Optional[List[str]] = None,
    ):
        renderer.empty_line()
        for command in commands:
            renderer.table.add_row(*command.summary)
        renderer.table.render()
        renderer.empty_line()
