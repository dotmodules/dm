from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


class HooksCommand(Command):
    @property
    def match_pattern(self) -> str:
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
        abort_interpreter: Callable[[], None],
        renderer: Renderer,
        commands: List[Command],
        parameters: Optional[List[str]] = None,
    ) -> None:
        renderer.empty_line()

        if len(modules) == 0:
            renderer.wrap.render("<<DIM>>You have no modules registered.<<RESET>>")
            renderer.empty_line()
            return

        if not parameters:
            index = 1
            for name, hooks in modules.aggregated_hooks.items():
                name_printed = False
                for hook in hooks:
                    hook_priority = hook.hook_priority
                    hook_module_name = hook.execution_context.module_name
                    hook_details = hook.hook_description

                    renderer.table.add_row(
                        f"<<BOLD>><<BLUE>>[{str(index)}]<<RESET>>"
                        if not name_printed
                        else "",
                        f"<<BOLD>>{name}<<RESET>>" if not name_printed else "",
                        f"<<DIM>>({hook_priority})<<RESET>>",
                        f"<<BOLD>>{hook_module_name}<<RESET>>",
                        f"<<DIM>>{hook_details}<<RESET>>",
                    )
                    name_printed = True
                index += 1

            renderer.table.render()

        else:
            hook_index = int(parameters[0]) - 1
            hook_name = list(modules.aggregated_hooks.keys())[hook_index]
            hooks = modules.aggregated_hooks[hook_name]
            for hook in hooks:
                hook.execute()

        renderer.empty_line()
