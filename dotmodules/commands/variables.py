from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


class VariablesCommand(Command):
    @property
    def match_pattern(self):
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
        abort_interpreter: Callable,
        renderer: Renderer,
        commands: List[Command],
        parameters: Optional[List[str]] = None,
    ):
        # for index, module in enumerate(modules.variables, start=1):
        #     renderer.rows.add_row(
        #         f"<<BOLD>><<YELLOW>>[{str(index)}]<<RESET>>",
        #         f"<<BOLD>>{module.name}<<RESET>>",
        #         f"<<DIM>><<UNDERLINE>>{str(module.root)}<<RESET>>",
        #     )
        # renderer.rows.commit_rows()
        print("variables")
