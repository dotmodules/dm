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

        if not parameters:
            index = 1
            for name, hooks in modules.hooks.items():
                name_printed = False
                for hook in hooks:
                    hook_priority = hook.get_priority()
                    hook_module_name = hook.get_module_name()
                    hook_details = hook.get_details()

                    renderer.table.add_row(
                        f"<<BOLD>><<BLUE>>[{str(index)}]<<RESET>>"
                        if not name_printed
                        else "",
                        f"<<BOLD>>{name}<<RESET>>" if not name_printed else "",
                        str(hook_priority),
                        f"<<BOLD>>{hook_module_name}<<RESET>>",
                        hook_details,
                    )
                    name_printed = True
                index += 1

            renderer.table.render()

        else:
            hook_index = int(parameters[0]) - 1
            hook_name = list(modules.hooks.keys())[hook_index]
            hooks = modules.hooks[hook_name]
            for hook in hooks:
                hook.execute(settings=settings)

        renderer.empty_line()
