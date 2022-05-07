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
        ...

    @abstractproperty
    def summary(self) -> List[str]:
        ...

    @property
    def is_default(self) -> bool:
        return False

    @abstractmethod
    def execute(
        self,
        settings: Settings,
        modules: Modules,
        abort_interpreter: Callable[[], None],
        renderer: Renderer,
        commands: List["Command"],
        parameters: Optional[List[str]] = None,
    ) -> None:
        ...


class Commands:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._command_objects = []
        self._default_command: Command

        for command_class in Command.__subclasses__():
            # MyPy identifies the 'command_class' subclass as the parent class
            # for some reason, and complains on instantiating an abstract
            # class..
            command_object = command_class(settings=self._settings)  # type: ignore
            if command_object.is_default:
                self._default_command = command_object
            self._command_objects.append(command_object)
        if not self._default_command:
            raise SystemError("default command wasn't set")

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

    def process_input(
        self,
        raw_input: str,
        abort_interpreter: Callable[[], None],
        modules: Modules,
        renderer: Renderer,
    ) -> None:
        command_name, parameters = self._parse_raw_input(raw_input=raw_input)

        if not command_name:
            self._default_command.execute(
                settings=self._settings,
                modules=modules,
                abort_interpreter=abort_interpreter,
                renderer=renderer,
                commands=self._command_objects,
                parameters=parameters,
            )
            return

        if matched_command := self._match_command_for_command_name(
            command_name=command_name
        ):
            matched_command.execute(
                settings=self._settings,
                modules=modules,
                abort_interpreter=abort_interpreter,
                renderer=renderer,
                commands=self._command_objects,
                parameters=parameters,
            )
        else:
            self._default_command.execute(
                settings=self._settings,
                modules=modules,
                abort_interpreter=abort_interpreter,
                renderer=renderer,
                commands=self._command_objects,
                parameters=parameters,
            )
