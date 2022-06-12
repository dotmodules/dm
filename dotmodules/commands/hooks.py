from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Modules
from dotmodules.modules.path import PathManager
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

        if not modules.modules:
            renderer.wrap.render("<<DIM>>You have no modules registered.<<RESET>>")
            renderer.empty_line()
            return

        if not parameters:
            index = 1
            for name, hook_aggregates in modules.hooks.items():
                name_printed = False
                for hook_aggregate in hook_aggregates:
                    hook_priority = hook_aggregate.hook.hook_priority
                    hook_module_name = hook_aggregate.module.name
                    hook_details = hook_aggregate.hook.hook_description

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
            hook_aggregates = modules.hooks[hook_name]
            for hook_aggregate in hook_aggregates:
                path_manager = PathManager(root_path=hook_aggregate.module.root)
                hook_aggregate.hook.execute(
                    module_name=hook_aggregate.module.name,
                    module_root=hook_aggregate.module.root,
                    path_manager=path_manager,
                    settings=settings,
                )

        renderer.empty_line()
