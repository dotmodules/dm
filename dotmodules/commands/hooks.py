from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


class HooksCommand(Command):
    @property
    def match_pattern(self):
        return self._settings.hotkey_hooks

    @property
    def summary(self) -> List[str]:
        return [
            f"<<BOLD>>[<<YELLOW>>{self._settings.hotkey_hooks}<<RESET>><<BOLD>>]<<RESET>>",
            "This is the hooks command.",
        ]

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

        index = 1
        for name, hooks in modules.hooks.items():
            name_printed = False
            for hook in hooks:
                renderer.table.add_row(
                    f"<<BOLD>><<BLUE>>[{str(index)}]<<RESET>>"
                    if not name_printed
                    else "",
                    f"<<BOLD>>{name}<<RESET>>" if not name_printed else "",
                    hook.priority,
                    f"<<BOLD>>{hook.module_name}<<RESET>>",
                    hook.path_to_script,
                )
                name_printed = True
            index += 1

        renderer.table.render()

        renderer.empty_line()
