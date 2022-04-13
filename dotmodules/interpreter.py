from dotmodules.commands import Commands
from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import load_settings


class InterpreterFinished(Exception):
    pass


class CommandLineInterpreter:
    def __init__(self):
        self._settings = load_settings()
        self._commands = Commands(settings=self._settings)
        self._renderer = Renderer(settings=self._settings)
        self._modules = Modules.load(
            modules_root_path=self._settings.relative_modules_path,
            config_file_name=self._settings.config_file_name,
        )

    def _abort_interpreter(self):
        raise InterpreterFinished()

    def run(self):
        prompt = self._renderer.prompt.render(
            prompt_template=self._settings.prompt_template
        )
        self._renderer.wrap.render(
            string=" <<BOLD>>dotmodules<<RESET>> <<DIM>>v1.0<<RESET>>",
            indent=False,
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
