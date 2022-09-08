from dotmodules.commands import Commands
from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings

DM_LOGO = """
      ██│
      ██│
      ██│
      ██│
      ██│
████████████████████│
██│   ██│   ██│   ██│
████████│   ██│   ██│
"""

DM_LOGO_COLOR_CODE = 106


class InterpreterFinished(Exception):
    pass


class CommandLineInterpreter:
    def __init__(
        self, settings: Settings, renderer: Renderer, modules: Modules
    ) -> None:
        self._settings = settings
        self._renderer = renderer
        self._modules = modules

        self._commands = Commands(settings=self._settings)

        for line in DM_LOGO.splitlines():
            self._renderer.wrap.render(
                string=f" <<{DM_LOGO_COLOR_CODE}>>{line}<<RESET>>", indent=False
            )
        self._renderer.empty_line()

        self._renderer.wrap.render(
            string=" <<BOLD>>dotmodules<<RESET>> <<DIM>>v1.0<<RESET>>",
            indent=False,
        )

    def _abort_interpreter(self) -> None:
        raise InterpreterFinished()

    def run(self) -> None:
        prompt = self._renderer.prompt.render(
            prompt_template=self._settings.prompt_template
        )

        while True:
            raw_input = input(prompt)
            try:
                self._commands.process_input(
                    raw_input=raw_input,
                    abort_interpreter=self._abort_interpreter,
                    modules=self._modules,
                    renderer=self._renderer,
                )
            except InterpreterFinished:
                break
