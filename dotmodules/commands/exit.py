from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


class ExitCommand(Command):
    @property
    def match_pattern(self) -> str:
        return self._settings.hotkey_exit

    @property
    def summary(self) -> List[str]:
        return [
            f"<<BOLD>>[<<RED>>{self._settings.hotkey_exit}<<RESET>><<BOLD>>]<<RESET>>",
            "Exists from the interpreter.",
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
        abort_interpreter()
