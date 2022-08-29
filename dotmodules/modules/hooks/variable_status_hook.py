from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, TypedDict, cast

from dotmodules.modules.hooks.base import (
    Hook,
    HookAdapterScript,
    HookExecutionContext,
    HookExecutionResult,
    HookExecutionType,
    SerializedHookExecutionContextDict,
)
from dotmodules.modules.path import PathManager


class VariableStatusHookExecutionMode(str, Enum):
    PREPARE = "prepare"
    EXECUTE = "execute"


class SerializedVariableStatusHooksDict(TypedDict):
    path_to_script: str
    variable_name: str
    prepare_step_necessary: bool
    execution_context: SerializedHookExecutionContextDict


@dataclass
class VariableStatusHook(Hook):
    """
    Specialized hook that can provide the status about the consumed variables in
    a variable consumer module.
    """

    path_to_script: str
    variable_name: str
    prepare_step_necessary: bool = False

    # Abstract Hook base class implementations.
    @property
    def hook_name(self) -> str:
        return f"VARIABLE_STATUS_HOOK[{self.variable_name}]"

    @property
    def hook_priority(self) -> int:
        return 0

    @property
    def hook_description(self) -> str:
        return f"Retrieves deployment statistics for variable '{self.variable_name}' through script <<UNDERLINE>>{self.path_to_script}<<RESET>>"

    @property
    def hook_execution_type(self) -> HookExecutionType:
        return HookExecutionType.CAPTURE

    @property
    def hook_adapter_script(self) -> HookAdapterScript:
        return HookAdapterScript.VARIABLE_STATUS

    def get_additional_hook_arguments(
        self,
        path_manager: PathManager,
        extra_arguments: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """
        It is expected that the caller process will pass three extra arguments
        as a dictionary in the 'extra_arguments' parameter. These extra
        arguments will be the execution mode, variable name and variable value
        in this order.
        """
        if extra_arguments:
            execution_mode = extra_arguments["execution_mode"]
            variable_name = extra_arguments["variable_name"]
            variable_value = extra_arguments["variable_value"]
            cache_path = extra_arguments["cache_path"]

        if variable_name != self.variable_name:
            raise ValueError(
                f"variable name mismatch! {variable_name} != {self.variable_name}"
            )

        return [
            # 9 - dm__config__execution_mode
            execution_mode,
            # 10 - dm__config__variable_name
            variable_name,
            # 11 - dm__config__variable_value
            variable_value,
            # 12 - dm__config__target_hook_script
            str(path_manager.resolve_local_path(self.path_to_script)),
            # 13 - dm__config__cache_path
            cache_path,
        ]

    # Abstract ErrorListProvider base class implementations.
    def report_errors(self, path_manager: PathManager) -> List[str]:
        """
        The path to script should be relative to the module root directory.
        """
        errors = []
        full_path = path_manager.resolve_local_path(self.path_to_script)
        if not full_path.is_file():
            message = f"VariableStatusHook[{self.variable_name}]: path_to_script '{self.path_to_script}' does not name a file!"
            errors.append(message)
        return errors

    def serialize(self) -> SerializedVariableStatusHooksDict:
        serialized_data = asdict(self)
        return cast(SerializedVariableStatusHooksDict, serialized_data)

    @classmethod
    def deserialize(
        cls, serialized_data: SerializedVariableStatusHooksDict
    ) -> "VariableStatusHook":
        serialized_execution_context = serialized_data["execution_context"]
        execution_context = HookExecutionContext(**serialized_execution_context)
        variable_status_hook = cls(
            path_to_script=serialized_data["path_to_script"],
            variable_name=serialized_data["variable_name"],
            prepare_step_necessary=serialized_data["prepare_step_necessary"],
        )
        variable_status_hook.execution_context = execution_context
        return variable_status_hook

    def execute_prepare_step(
        self, variable_name: str, cache_path: Path
    ) -> HookExecutionResult:
        return self.execute(
            extra_arguments={
                "execution_mode": VariableStatusHookExecutionMode.PREPARE,
                "variable_name": variable_name,
                "variable_value": "",
                "cache_path": str(cache_path),
            },
        )

    def execute_execute_step(
        self, variable_name: str, variable_value: str, cache_path: Path
    ) -> HookExecutionResult:
        return self.execute(
            extra_arguments={
                "execution_mode": VariableStatusHookExecutionMode.EXECUTE,
                "variable_name": variable_name,
                "variable_value": variable_value,
                "cache_path": str(cache_path),
            },
        )
