import os
from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Module, Modules, ModuleStatus
from dotmodules.modules.path import PathManager
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
                "<<DIM>><<CYAN>>These are the modules available in your configuration. "
                "You can select a module by appending its index to the modules "
                f"command like {settings.hotkey_modules} 42.<<RESET>>"
            )
            renderer.empty_line()

            if not modules.modules:
                renderer.wrap.render("<<DIM>>You have no modules registered.<<RESET>>")
                renderer.empty_line()
                return

            for index, module in enumerate(modules.modules, start=1):
                root = os.path.relpath(
                    module.root, settings.relative_modules_path.resolve()
                )

                # TODO: After the minimum supported python version became 3.10
                # we can uncomment this more elegant syntax..
                # match module.status:
                #     case ModuleStatus.DISABLED:
                #         status = "<<BOLD>><<RED>>disabled<<RESET>>"
                #     case ModuleStatus.PENDING:
                #         status = "<<BOLD>><<YELLOW>>pending<<RESET>>"
                #     case ModuleStatus.DEPLOYED:
                #         status = "<<BOLD>><<GREEN>>deployed<<RESET>>"
                #     case ModuleStatus.ERROR:
                #         status = "<<BOLD>><<RED>>error<<RESET>>"
                #     case _:
                #         raise ValueError(f"Invalid module status value: '{module.status}'")

                if module.status == ModuleStatus.DISABLED:
                    status = "<<BOLD>><<RED>>disabled<<RESET>>"
                elif module.status == ModuleStatus.PENDING:
                    status = "<<BOLD>><<YELLOW>>pending<<RESET>>"
                elif module.status == ModuleStatus.DEPLOYED:
                    status = "<<BOLD>><<GREEN>>deployed<<RESET>>"
                elif module.status == ModuleStatus.ERROR:
                    status = "<<BOLD>><<RED>>error<<RESET>>"
                else:
                    raise ValueError(f"Invalid module status value: '{module.status}'")

                renderer.table.add_row(
                    f"<<BOLD>><<BLUE>>[{str(index)}]<<RESET>>",
                    f"<<BOLD>>{module.name}<<RESET>>",
                    f"{str(module.version)}",
                    status,
                    f"<<UNDERLINE>>{str(root)}<<RESET>>",
                )
                renderer.table.add_row("", "", "", "", "")
            renderer.table.render()

        elif len(parameters) == 1:

            if not modules.modules:
                renderer.wrap.render("<<DIM>>You have no modules registered.<<RESET>>")
                renderer.empty_line()
                return

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
            self._render_module_errors(
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
            path_manager = PathManager(root_path=module.root)

            hook_status_code = hook.execute(
                module_name=module.name,
                module_root=module.root,
                path_manager=path_manager,
                settings=self._settings,
            )

            if hook_status_code != 0:
                renderer.empty_line()
                renderer.wrap.render(
                    f"<<RED>>Hook failed with status code <<BOLD>>{hook_status_code}<<RESET>><<RED>>!<<RESET>>"
                )

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

        # TODO: After the minimum supported python version became 3.10
        # we can uncomment this more elegant syntax..
        # match module.status:
        #     case ModuleStatus.DISABLED:
        #         status = "<<BOLD>><<RED>>disabled<<RESET>>"
        #     case ModuleStatus.PENDING:
        #         status = "<<BOLD>><<YELLOW>>pending<<RESET>>"
        #     case ModuleStatus.DEPLOYED:
        #         status = "<<BOLD>><<GREEN>>deployed<<RESET>>"
        #     case ModuleStatus.ERROR:
        #         status = "<<BOLD>><<RED>>error<<RESET>>"
        #     case _:
        #         raise ValueError(f"Invalid module status value: '{module.status}'")

        if module.status == ModuleStatus.DISABLED:
            status = "<<BOLD>><<RED>>disabled<<RESET>>"
        elif module.status == ModuleStatus.PENDING:
            status = "<<BOLD>><<YELLOW>>pending<<RESET>>"
        elif module.status == ModuleStatus.DEPLOYED:
            status = "<<BOLD>><<GREEN>>deployed<<RESET>>"
        elif module.status == ModuleStatus.ERROR:
            status = "<<BOLD>><<RED>>error<<RESET>>"
        else:
            raise ValueError(f"Invalid module status value: '{module.status}'")
        text = renderer.wrap.render(
            string=status,
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

    def _render_module_errors(
        self, renderer: Renderer, module: Module, settings: Settings
    ) -> None:
        if module.errors:
            renderer.empty_line()
            text = []
            for error in module.errors:
                text += renderer.wrap.render(
                    string=f"<<BOLD>><<RED>>{error}<<RESET>>",
                    wrap_limit=settings.body_width,
                    print_lines=False,
                    indent=False,
                )
            renderer.header.render(
                header="<<DIM>>Errors<<RESET>>",
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
        path_manager = PathManager(root_path=module.root)

        for link in module.links:
            link_color = "RED"
            target_color = "RED"

            try:
                if link.check_if_link_exists(path_manager=path_manager):
                    link_color = "GREEN"
                    if link.check_if_target_matched(path_manager=path_manager):
                        target_color = "GREEN"
                link_status = f"<<BOLD>><<{link_color}>>link<<RESET>>"
                target_status = f"<<BOLD>><<{target_color}>>target<<RESET>>"
                status = f"<<DIM>>[<<RESET>>{link_status}<<DIM>>|<<RESET>>{target_status}<<DIM>>]<<RESET>>"
            except ValueError:
                status = "<<DIM>>[<<RESET>>   <<BOLD>><<RED>>error<<RESET>>   <<DIM>>]<<RESET>>"

            renderer.table.add_row(
                status,
                f"<<UNDERLINE>>{link.path_to_target}<<RESET>>",
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
            renderer.table.add_row(
                f"<<BOLD>><<BLUE>>[{index}]<<RESET>>",
                f"<<BOLD>>{hook.hook_name}<<RESET>> ({hook.hook_priority})",
                f"{hook.hook_description}",
            )
        text = renderer.table.render(print_lines=False, indent=False)

        renderer.header.render(
            header="<<DIM>>Hooks<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.header_separator,
        )
