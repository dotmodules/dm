import os
from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Module, Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


class ModulesCommand(Command):
    @property
    def match_pattern(self) -> str:
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
        abort_interpreter: Callable[[], None],
        renderer: Renderer,
        commands: List[Command],
        parameters: Optional[List[str]] = None,
    ) -> None:

        renderer.empty_line()

        if not parameters:
            renderer.wrap.render(
                "<<DIM>>These are the modules available in your configuration. "
                "You can select a module by appending its index to the modules "
                f"command like {settings.hotkey_modules} 42.<<RESET>>"
            )
            renderer.empty_line()
            for index, module in enumerate(modules.modules, start=1):
                root = os.path.relpath(
                    module.root, settings.relative_modules_path.resolve()
                )
                renderer.table.add_row(
                    f"<<BOLD>><<BLUE>>[{str(index)}]<<RESET>>",
                    f"<<BOLD>>{module.name}<<RESET>>",
                    f"{str(module.version)}",
                    "<<BOLD>><<GREEN>>deployed<<RESET>>",
                    f"<<UNDERLINE>>{str(root)}<<RESET>>",
                )
            renderer.table.render()

        elif len(parameters) == 1:
            index = int(parameters[0])
            module = modules.modules[index - 1]

            self._render_module_name(
                renderer=renderer, module=module, settings=settings
            )
            self._render_module_version(
                renderer=renderer, module=module, settings=settings
            )
            self._render_module_status(
                renderer=renderer, module=module, settings=settings
            )
            self._render_module_documentation(
                renderer=renderer, module=module, settings=settings
            )
            self._render_module_path(
                renderer=renderer, module=module, settings=settings
            )
            self._render_module_variables(
                renderer=renderer, module=module, settings=settings
            )
            self._render_module_links(
                renderer=renderer, module=module, settings=settings
            )
            self._render_module_hooks(
                renderer=renderer, module=module, settings=settings
            )

        elif len(parameters) == 2:
            module_index = int(parameters[0]) - 1
            hook_index = int(parameters[1]) - 1

            module = modules.modules[module_index]
            hook = module.hooks[hook_index]

            hook_status_code = hook.execute(settings=self._settings)

            if hook_status_code != 0:
                raise ValueError("hook failed")

        renderer.empty_line()

    def _render_module_name(
        self, renderer: Renderer, module: Module, settings: Settings
    ) -> None:
        text = renderer.wrap.render(
            string=f"<<BOLD>>{module.name}<<RESET>>",
            wrap_limit=settings.body_width,
            print_lines=False,
            indent=False,
        )
        renderer.header.render(
            header="<<DIM>>Name<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.header_separator,
        )

    def _render_module_version(
        self, renderer: Renderer, module: Module, settings: Settings
    ) -> None:
        renderer.empty_line()
        text = renderer.wrap.render(
            string=module.version,
            wrap_limit=settings.body_width,
            print_lines=False,
            indent=False,
        )
        renderer.header.render(
            header="<<DIM>>Version<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.header_separator,
        )

    def _render_module_status(
        self, renderer: Renderer, module: Module, settings: Settings
    ) -> None:
        renderer.empty_line()
        text = renderer.wrap.render(
            string="<<BOLD>><<GREEN>>deployed<<RESET>>",
            wrap_limit=settings.body_width,
            print_lines=False,
            indent=False,
        )
        renderer.header.render(
            header="<<DIM>>Status<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.header_separator,
        )

    def _render_module_documentation(
        self, renderer: Renderer, module: Module, settings: Settings
    ) -> None:
        renderer.empty_line()
        text = renderer.wrap.render(
            string="\n".join(module.documentation),
            wrap_limit=settings.body_width,
            print_lines=False,
            indent=False,
        )
        renderer.header.render(
            header="<<DIM>>Docs<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.header_separator,
        )

    def _render_module_path(
        self, renderer: Renderer, module: Module, settings: Settings
    ) -> None:
        renderer.empty_line()
        text = renderer.wrap.render(
            string=f"<<UNDERLINE>>{str(module.root)}<<RESET>>",
            wrap_limit=settings.body_width,
            print_lines=False,
            indent=False,
        )
        renderer.header.render(
            header="<<DIM>>Path<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.header_separator,
        )

    def _render_module_links(
        self, renderer: Renderer, module: Module, settings: Settings
    ) -> None:
        if not module.links:
            return

        renderer.empty_line()

        for link in module.links:
            link_color = "RED"
            target_color = "RED"
            if link.present:
                link_color = "GREEN"
                if link.target_matched:
                    target_color = "GREEN"

            link_status = f"<<BOLD>><<{link_color}>>link<<RESET>>"
            target_status = f"<<BOLD>><<{target_color}>>target<<RESET>>"

            status = f"<<DIM>>[<<RESET>>{link_status}<<DIM>>|<<RESET>>{target_status}<<DIM>>]<<RESET>>"

            renderer.table.add_row(
                status,
                f"<<UNDERLINE>>{link.path_to_file}<<RESET>>",
                f"<<UNDERLINE>>{link.path_to_symlink}<<RESET>>",
            )
        text = renderer.table.render(print_lines=False, indent=False)
        renderer.header.render(
            header="<<DIM>>Links<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.header_separator,
        )

    def _render_module_variables(
        self, renderer: Renderer, module: Module, settings: Settings
    ) -> None:
        if not module.variables:
            return

        renderer.empty_line()

        for name, values in module.variables.items():
            renderer.table.add_row(
                f"<<BOLD>>{name}<<RESET>> " + " ".join(values),
            )
        text = renderer.table.render(print_lines=False, indent=False)

        renderer.header.render(
            header="<<DIM>>Variables<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.header_separator,
        )

    def _render_module_hooks(
        self, renderer: Renderer, module: Module, settings: Settings
    ) -> None:
        if not module.hooks:
            return

        renderer.empty_line()

        for index, hook in enumerate(module.hooks, start=1):
            hook_name = hook.get_name()
            hook_priority = hook.get_priority()
            hook_details = hook.get_details()

            renderer.table.add_row(
                f"<<BOLD>><<BLUE>>[{index}]<<RESET>>",
                f"<<BOLD>>{hook_name}<<RESET>> ({hook_priority})",
                f"<<UNDERLINE>>{hook_details}<<RESET>>",
            )
        text = renderer.table.render(print_lines=False, indent=False)

        renderer.header.render(
            header="<<DIM>>Hooks<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.header_separator,
        )
