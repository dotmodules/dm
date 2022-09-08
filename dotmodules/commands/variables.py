from typing import Callable, List, Optional

from dotmodules.commands import Command
from dotmodules.modules import Modules
from dotmodules.modules.variable_status import VariableStatusValue
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


class VariablesCommand(Command):
    @property
    def match_pattern(self) -> str:
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

        header_width = max(
            [len(name) for name in modules.aggregated_variables.keys()]
        ) + len(settings.rendered_column_padding)
        body_width = (
            settings.text_wrap_limit
            - header_width
            - len(settings.rendered_column_padding)
        )
        header_separator = " "

        for name, values in modules.aggregated_variables.items():
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

            text = renderer.wrap.render(
                string=" ".join(prepared_values),
                wrap_limit=body_width,
                print_lines=False,
                indent=False,
            )
            renderer.header.render(
                header=f"<<BOLD>>{name}<<RESET>>",
                header_width=header_width,
                lines=text,
                separator=header_separator,
            )

        renderer.empty_line()
