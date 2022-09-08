import os
from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Module, Modules, ModuleStatus
from dotmodules.modules.path import PathManager
from dotmodules.modules.variable_status import VariableStatusValue
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

    def render_list(
        self, modules: Modules, settings: Settings, renderer: Renderer
    ) -> None:
        renderer.wrap.render(
            "<<DIM>><<CYAN>>These are the modules available in your configuration. "
            "You can select a module by appending its index to the modules "
            f"command like {settings.hotkey_modules} 42.<<RESET>>"
        )
        renderer.empty_line()

        if len(modules) == 0:
            renderer.wrap.render("<<DIM>>You have no modules registered.<<RESET>>")
            renderer.empty_line()
            return

        current_root = ""
        for index, module in enumerate(modules, start=1):
            root = os.path.relpath(
                module.root, settings.relative_modules_path.resolve()
            )
            base_root = os.path.dirname(root)

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
                color = "<<DIM>>"
            elif module.status == ModuleStatus.INCOMPLETE:
                color = "<<BOLD>><<YELLOW>>"
            elif module.status == ModuleStatus.DEPLOYED:
                color = "<<BOLD>><<GREEN>>"
            elif module.status == ModuleStatus.ERROR:
                color = "<<BOLD>><<RED>>"
            elif module.status == ModuleStatus.LOADING:
                color = "<<BOLD>><<MAGENTA>>"
            else:
                raise ValueError(f"Invalid module status value: '{module.status}'")

            status = f"{color}{module.status.value}<<RESET>>"

            if not current_root:
                current_root = base_root
            elif current_root != base_root:
                current_root = base_root
                renderer.table.add_row("", "", "", "", "")

            index_column = (
                f"<<BOLD>><<BLUE>>[{str(index)}]<<RESET>>"
                if not module.is_disabled
                else f"<<DIM>>[{str(index)}]<<RESET>>"
            )
            if module.is_disabled:
                name_column = f"<<DIM>>{module.name}<<RESET>>"
            elif module.is_incomplete:
                name_column = f"<<BOLD>><<YELLOW>>{module.name}<<RESET>>"
            else:
                name_column = f"<<BOLD>>{module.name}<<RESET>>"

            version_column = (
                f"{str(module.version)}"
                if not module.is_disabled
                else f"<<DIM>>{str(module.version)}<<RESET>>"
            )
            root_column = (
                f"<<UNDERLINE>>{str(root)}<<RESET>>"
                if not module.is_disabled
                else f"<<UNDERLINE>><<DIM>>{str(root)}<<RESET>>"
            )

            renderer.table.add_row(
                index_column,
                name_column,
                version_column,
                status,
                root_column,
            )

        renderer.table.render()

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
            self.render_list(modules=modules, settings=settings, renderer=renderer)

        elif len(parameters) == 1:
            if len(modules) == 0:
                renderer.wrap.render("<<DIM>>You have no modules registered.<<RESET>>")
                renderer.empty_line()
                return

            index = int(parameters[0])
            module = modules[index - 1]

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
                renderer=renderer, modules=modules, module=module, settings=settings
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

            module = modules[module_index]
            hook = module.hooks[hook_index]

            hook_status_code = hook.execute()

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
            separator=settings.rendered_header_separator,
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
            separator=settings.rendered_header_separator,
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
            color = "<<DIM>>"
        elif module.status == ModuleStatus.INCOMPLETE:
            color = "<<BOLD>><<YELLOW>>"
        elif module.status == ModuleStatus.DEPLOYED:
            color = "<<BOLD>><<GREEN>>"
        elif module.status == ModuleStatus.ERROR:
            color = "<<BOLD>><<RED>>"
        elif module.status == ModuleStatus.LOADING:
            color = "<<BOLD>><<MAGENTA>>"
        else:
            raise ValueError(f"Invalid module status value: '{module.status}'")

        status = f"{color}{module.status.value}<<RESET>>"

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
            separator=settings.rendered_header_separator,
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
                separator=settings.rendered_header_separator,
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
            separator=settings.rendered_header_separator,
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
            separator=settings.rendered_header_separator,
        )

    def _render_module_links(
        self, renderer: Renderer, module: Module, settings: Settings
    ) -> None:
        if not module.links:
            return

        renderer.empty_line()
        path_manager = PathManager(root_path=module.root)

        for link in module.links:
            link_exists = link.check_if_link_exists(path_manager=path_manager)
            target_matched = link.check_if_target_matched(path_manager=path_manager)

            if link_exists and target_matched:
                path_to_symlink_color = "<<BOLD>><<GREEN>>"
                link_status = "<<DIM>>==><<RESET>>"
                path_to_target_color = "<<BOLD>><<GREEN>>"
                target_status = "<<DIM>>[matched]<<RESET>>"

            elif link_exists and not target_matched:
                path_to_symlink_color = "<<BOLD>><<GREEN>>"
                link_status = "<<DIM>>=X=<<RESET>>"
                path_to_target_color = "<<BOLD>><<RED>>"
                target_status = "<<DIM>>[mismatch]<<RESET>>"

            elif not link_exists:
                path_to_symlink_color = "<<BOLD>><<RED>>"
                link_status = ""
                path_to_target_color = "<<BOLD>><<RED>>"
                target_status = "<<DIM>>[missing]<<RESET>>"

            renderer.table.add_row(
                f"<<BOLD>>{link.name}<<RESET>>",
                f"<<UNDERLINE>>{path_to_symlink_color}{link.path_to_symlink}<<RESET>>",
                link_status,
                f"<<UNDERLINE>>{path_to_target_color}{link.path_to_target}<<RESET>>",
                target_status,
            )
        text = renderer.table.render(print_lines=False, indent=False)
        renderer.header.render(
            header="<<DIM>>Links<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.rendered_header_separator,
        )

    def _render_module_variables(
        self, renderer: Renderer, modules: Modules, module: Module, settings: Settings
    ) -> None:
        if not module.variables:
            return

        renderer.empty_line()

        for name, values in module.variables.items():
            prepared_values = []
            for value in values:
                variable_status = modules.variable_statuses.get(
                    variable_name=name, variable_value=value
                )
                if variable_status.status == VariableStatusValue.ADDED:
                    color = "<<GREEN>>"
                elif variable_status.status == VariableStatusValue.MISSING:
                    color = "<<RED>>"
                elif variable_status.status == VariableStatusValue.LOADING:
                    color = "<<MAGENTA>>"
                elif variable_status.status == VariableStatusValue.NOT_AVAIBLE:
                    color = "<<DIM>>"
                else:
                    raise ValueError(
                        f"Invalid variable status value: '{variable_status.status}'"
                    )

                prepared_values.append(
                    f"<<BOLD>>{color}[{value}]<<RESET>><<DIM>>-{variable_status.status_string}<<RESET>>"
                )
            renderer.table.add_row(
                f"<<BOLD>>{name}<<RESET>> " + " ".join(prepared_values),
            )
        text = renderer.table.render(print_lines=False, indent=False)

        renderer.header.render(
            header="<<DIM>>Variables<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.rendered_header_separator,
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
                f"<<BOLD>>{hook.hook_name}<<RESET>> <<DIM>>({hook.hook_priority})<<RESET>>",
                f"<<DIM>>{hook.hook_description}<<RESET>>",
            )
        text = renderer.table.render(print_lines=False, indent=False)

        renderer.header.render(
            header="<<DIM>>Hooks<<RESET>>",
            header_width=settings.header_width,
            lines=text,
            separator=settings.rendered_header_separator,
        )
