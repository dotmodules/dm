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
        renderer.wrap.render(
            "<<BLUE>>These are the modules available in your configuration. "
            "You can select a module by appending its index to the modules "
            f"command like {settings.hotkey_modules} 42.<<RESET>>"
        )
        if not parameters:
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
            renderer.empty_line()
            return
        else:
            index = int(parameters[0])
            module = modules.modules[index - 1]
            print(module.name)
            print(module.version)
            import textwrap

            for line in module.documentation:
                wrapped = "\n".join(textwrap.wrap(line, width=settings.text_wrap_limit))
                print(wrapped)
            print(f"links: {module.links}")
            print(f"variables: {module.variables}")
            print(f"hooks: {module.hooks}")
