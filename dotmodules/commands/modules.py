from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Module, Modules
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
                renderer.table.add_row(
                    f"<<DIM>>[{str(index)}]<<RESET>>",
                    f"<<BOLD>>{module.name}<<RESET>>",
                    f"{str(module.version)}",
                    "<<BOLD>><<GREEN>>deployed<<RESET>>",
                    f"<<UNDERLINE>>{str(module.root)}<<RESET>>",
                )
            renderer.table.render()

        else:
            header_width = 10
            body_width = (
                settings.text_wrap_limit - header_width - len(settings.column_padding)
            )
            header_separator = "  "

            index = int(parameters[0])
            module = modules.modules[index - 1]

            section_data = {
                "renderer": renderer,
                "module": module,
                "header_width": header_width,
                "body_width": body_width,
                "header_separator": header_separator,
            }

            self._render_module_name(section_data=section_data)
            self._render_module_path(section_data=section_data)
            self._render_module_version(section_data=section_data)
            renderer.empty_line()
            self._render_module_status(section_data=section_data)
            renderer.empty_line()
            self._render_module_documentation(section_data=section_data)
            renderer.empty_line()
            self._render_module_links(section_data=section_data)
            renderer.empty_line()
            self._render_module_variables(section_data=section_data)
            renderer.empty_line()
            self._render_module_hooks(section_data=section_data)

        renderer.empty_line()

    def _render_module_name(self, section_data: dict):
        renderer: Renderer = section_data["renderer"]
        module: Module = section_data["module"]
        header_width: int = section_data["header_width"]
        body_width: int = section_data["body_width"]
        header_separator: str = section_data["header_separator"]

        text = renderer.wrap.render(
            string=f"<<BOLD>>{module.name}<<RESET>>",
            wrap_limit=body_width,
            return_lines=True,
            indent=False,
        )
        renderer.header.render(
            header="<<DIM>>Name<<RESET>>",
            header_width=header_width,
            lines=text,
            separator=header_separator,
        )

    def _render_module_version(self, section_data: dict):
        renderer: Renderer = section_data["renderer"]
        module: Module = section_data["module"]
        header_width: int = section_data["header_width"]
        body_width: int = section_data["body_width"]
        header_separator: str = section_data["header_separator"]

        text = renderer.wrap.render(
            string=module.version,
            wrap_limit=body_width,
            return_lines=True,
            indent=False,
        )
        renderer.header.render(
            header="<<DIM>>Version<<RESET>>",
            header_width=header_width,
            lines=text,
            separator=header_separator,
        )

    def _render_module_status(self, section_data: dict):
        renderer: Renderer = section_data["renderer"]
        header_width: int = section_data["header_width"]
        body_width: int = section_data["body_width"]
        header_separator: str = section_data["header_separator"]

        text = renderer.wrap.render(
            string="<<BOLD>><<GREEN>>deployed<<RESET>>",
            wrap_limit=body_width,
            return_lines=True,
            indent=False,
        )
        renderer.header.render(
            header="<<DIM>>Status<<RESET>>",
            header_width=header_width,
            lines=text,
            separator=header_separator,
        )

    def _render_module_documentation(self, section_data: dict):
        renderer: Renderer = section_data["renderer"]
        module: Module = section_data["module"]
        header_width: int = section_data["header_width"]
        body_width: int = section_data["body_width"]
        header_separator: str = section_data["header_separator"]

        text = renderer.wrap.render(
            string="\n".join(module.documentation),
            wrap_limit=body_width,
            return_lines=True,
            indent=False,
        )
        renderer.header.render(
            header="<<DIM>>Docs<<RESET>>",
            header_width=header_width,
            lines=text,
            separator=header_separator,
        )

    def _render_module_path(self, section_data: dict):
        renderer: Renderer = section_data["renderer"]
        module: Module = section_data["module"]
        header_width: int = section_data["header_width"]
        body_width: int = section_data["body_width"]
        header_separator: str = section_data["header_separator"]

        text = renderer.wrap.render(
            string=str(module.root),
            wrap_limit=body_width,
            return_lines=True,
            indent=False,
        )
        renderer.header.render(
            header="<<DIM>>Path<<RESET>>",
            header_width=header_width,
            lines=text,
            separator=header_separator,
        )

    def _render_module_links(self, section_data: dict):
        renderer: Renderer = section_data["renderer"]
        module: Module = section_data["module"]
        header_width: int = section_data["header_width"]
        header_separator: str = section_data["header_separator"]

        for link in module.links:
            renderer.table.add_row(
                "<<BOLD>>[<<GREEN>>link<<RESET>><<BOLD>>-<<RED>>target<<RESET>><<BOLD>>]<<RESET>>",
                link.path_to_file,
                link.path_to_symlink,
            )
        text = renderer.table.render(return_lines=True, indent=False)
        renderer.header.render(
            header="Links",
            header_width=header_width,
            lines=text,
            separator=header_separator,
        )

    def _render_module_variables(self, section_data: dict):
        renderer: Renderer = section_data["renderer"]
        module: Module = section_data["module"]
        header_width: int = section_data["header_width"]
        header_separator: str = section_data["header_separator"]

        for name, values in module.variables.items():
            renderer.table.add_row(
                f"<<BOLD>><<UNDERLINE>>{name}<<RESET>> " + " ".join(values),
            )
        text = renderer.table.render(return_lines=True, indent=False)

        renderer.header.render(
            header="<<DIM>>Variables<<RESET>>",
            header_width=header_width,
            lines=text,
            separator=header_separator,
        )

    def _render_module_hooks(self, section_data: dict):
        renderer: Renderer = section_data["renderer"]
        module: Module = section_data["module"]
        header_width: int = section_data["header_width"]
        header_separator: str = section_data["header_separator"]

        for index, hook in enumerate(module.hooks, start=1):
            renderer.table.add_row(
                f"<<DIM>>[{index}]<<RESET>>",
                f"<<BOLD>><<UNDERLINE>>{hook.name}<<RESET>> [{hook.priority}]",
                hook.path_to_script,
            )
        text = renderer.table.render(return_lines=True, indent=False)

        renderer.header.render(
            header="<<DIM>>Hooks<<RESET>>",
            header_width=header_width,
            lines=text,
            separator=header_separator,
        )
