import re
from abc import ABC, abstractmethod, abstractproperty
from typing import Callable, List, Optional, Tuple

from dotmodules.modules import Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


class Command(ABC):
    def __init__(self, settings: Settings):
        self._settings = settings
        self.__pattern = re.compile(self.match_pattern)

    def match_command(self, command_string: str) -> bool:
        return bool(self.__pattern.match(command_string))

    @abstractproperty
    def match_pattern(self) -> str:
        pass

    @abstractproperty
    def summary(self) -> str:
        pass

    @abstractmethod
    def execute(
        self,
        modules: Modules,
        abort_interpreter: Callable,
        renderer: Renderer,
        parameters: Optional[List[str]] = None,
    ):
        pass


class ExitCommand(Command):
    @property
    def match_pattern(self):
        return self._settings.hotkey_exit

    @property
    def summary(self) -> str:
        return f"[{self._settings.hotkey_exit}] This is the exit command."

    def execute(
        self,
        modules: Modules,
        abort_interpreter: Callable,
        renderer: Renderer,
        parameters: Optional[List[str]] = None,
    ):
        abort_interpreter()


class ModulesCommand(Command):
    @property
    def match_pattern(self):
        return self._settings.hotkey_modules

    @property
    def summary(self) -> str:
        return f"[{self._settings.hotkey_modules}] This is the modules command."

    def execute(
        self,
        modules: Modules,
        abort_interpreter: Callable,
        renderer: Renderer,
        parameters: Optional[List[str]] = None,
    ):
        for index, module in enumerate(modules.modules, start=1):
            renderer.add_row(
                values=[
                    str(index),
                    module.name,
                    str(module.root),
                ],
                styles=[
                    renderer.STYLE__DEFAULT__LEFT,
                    renderer.STYLE__DEFAULT__LEFT,
                    renderer.STYLE__DEFAULT__LEFT,
                ],
            )
        renderer.commit_rows()


class Commands:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._command_objects = []
        for command_class in Command.__subclasses__():
            # MyPy identifies the 'command_class' subclass as the parent class
            # for some reason, and complains on instantiating an abstract
            # class..
            command_object = command_class(settings=self._settings)  # type: ignore
            self._command_objects.append(command_object)

    def _parse_raw_input(
        self, raw_input: str
    ) -> Tuple[Optional[str], Optional[List[str]]]:
        tokens = [item.strip() for item in raw_input.split()]
        if not tokens:
            return None, None
        if len(tokens) == 1:
            return tokens[0], None
        return tokens[0], tokens[1:]

    def _match_command_for_command_name(self, command_name: str) -> Optional[Command]:
        matched = []
        for command_object in self._command_objects:
            if command_object.match_command(command_string=command_name):
                matched.append(command_object)
        if matched:
            # TODO: report error on multiple matches.
            return matched[0]
        else:
            return None

    def _display_help(self):
        for command_object in self._command_objects:
            print(command_object.summary)

    def process_input(
        self,
        raw_input: str,
        abort_interpreter: Callable,
        modules: Modules,
        renderer: Renderer,
    ):
        command_name, parameters = self._parse_raw_input(raw_input=raw_input)

        if not command_name:
            self._display_help()
            return

        if matched_command := self._match_command_for_command_name(
            command_name=command_name
        ):
            matched_command.execute(
                modules=modules,
                abort_interpreter=abort_interpreter,
                renderer=renderer,
                parameters=parameters,
            )
        else:
            self._display_help()
