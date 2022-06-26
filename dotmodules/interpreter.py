import re
import shutil
from typing import Dict, List

from dotmodules.commands import Commands
from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import load_settings

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
    def __init__(self) -> None:
        self._settings = load_settings()
        self._commands = Commands(settings=self._settings)
        self._renderer = Renderer(settings=self._settings)
        self._modules = Modules.load(
            modules_root_path=self._settings.relative_modules_path,
            config_file_name=self._settings.config_file_name,
        )
        self._delete_cache()
        self._populate_variables_cache(self._modules.variables)

    def _delete_cache(self) -> None:
        cache_directory = self._settings.dm_cache_root
        shutil.rmtree(cache_directory, ignore_errors=True)

    def _populate_variables_cache(self, variables: Dict[str, List[str]]) -> None:
        variables_cache_directory = self._settings.dm_cache_variables
        variables_cache_directory.mkdir(parents=True)
        for name, values in variables.items():
            if re.search(r"\s", name):
                raise ValueError(
                    f"varibale name should not contain whitespace: '{name}'"
                )
            with open(variables_cache_directory / name, "w+") as f:
                for value in values:
                    f.write(f"{value}\n")

    def _abort_interpreter(self) -> None:
        raise InterpreterFinished()

    def run(self) -> None:
        prompt = self._renderer.prompt.render(
            prompt_template=self._settings.prompt_template
        )

        for line in DM_LOGO.splitlines():
            self._renderer.wrap.render(
                string=f" <<{DM_LOGO_COLOR_CODE}>>{line}<<RESET>>", indent=False
            )
        self._renderer.empty_line()

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
