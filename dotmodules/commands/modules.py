from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


class ModulesCommand(Command):
    @property
    def match_pattern(self):
        return self._settings.hotkey_modules

    @property
    def summary(self) -> List[str]:
        return [
            f"<<BOLD>>[<<YELLOW>>{self._settings.hotkey_modules}<<RESET>><<BOLD>>]<<RESET>>",
            "This is the modules command.",
        ]

    def execute(
        self,
        settings: Settings,
        modules: Modules,
        abort_interpreter: Callable,
        renderer: Renderer,
        commands: List[Command],
        parameters: Optional[List[str]] = None,
    ) -> None:

        renderer.empty_line()

        if not parameters:
            renderer.wrap.render(
                "<<BLUE>>These are the modules available in your configuration. "
                "You can select a module by appending its index to the modules "
                f"command like {settings.hotkey_modules} 42.<<RESET>>"
            )
            renderer.empty_line()
            for index, module in enumerate(modules.modules, start=1):
                renderer.rows.add_row(
                    f"<<DIM>>[{str(index)}]<<RESET>>",
                    f"<<BOLD>>{module.name}<<RESET>>",
                    f"{str(module.version)}",
                    "<<BOLD>><<GREEN>>deployed<<RESET>>",
                    f"<<UNDERLINE>>{str(module.root)}<<RESET>>",
                )
            renderer.rows.render_rows()

        else:
            index = int(parameters[0])
            module = modules.modules[index - 1]
            renderer.wrap.render(string=module.name)
            renderer.wrap.render(string=module.version)
            renderer.wrap.render(string="\n".join(module.documentation))

            renderer.empty_line()

            for link in module.links:
                renderer.rows.add_row(link.path_to_file, link.path_to_symlink)
            renderer.rows.render_rows()
            # renderer.wrap.render(string=module.links)
            # renderer.wrap.render(string=module.variables)
            # renderer.wrap.render(string=module.hooks)

        renderer.empty_line()
