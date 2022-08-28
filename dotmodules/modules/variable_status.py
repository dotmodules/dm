import json
import sys
import uuid
from collections import defaultdict
from pathlib import Path

# Importing and using the subprocess module can be a security issue, but it is
# necessary in our case.
from subprocess import Popen  # nosec
from typing import Dict, List, Optional, TypedDict

from dotmodules.modules.hooks import VariableStatus, VariableStatusHook
from dotmodules.modules.types import (
    AggregatedVariableStatusesType,
    AggregatedVariableStatusHooksType,
    AggregatedVariablesType,
)
from dotmodules.settings import Settings


class ShellResultDict(TypedDict):
    processed: bool
    status_string: str


AggregatedShellResultDictType = Dict[str, ShellResultDict]


class VariableStatusRefreshTask:
    REFRESH_TASK_SCRIPT_PATH = Path.cwd() / "dm_variable_status_worker.py"
    TRANSFER_FILE_NAME = "serialized_task_object.json"
    RESULT_FILE_NAME = "result.json"

    def __init__(
        self,
        task_id: str,
        variable_name: str,
        variable_values: List[str],
        variable_status_hook: VariableStatusHook,
        cache_path: Path,
    ) -> None:
        # Generating the unique id for the task.
        if not task_id:
            self._task_id = uuid.uuid4().hex
        else:
            self._task_id = task_id

        # Creating the cache directory for the task.
        self._cache_path = cache_path
        self._cache_path.mkdir(parents=True, exist_ok=True)

        # Assigning target variables.
        self._variable_name = variable_name
        self._variable_values = variable_values
        self._variable_status_hook = variable_status_hook

        # Empty result variable.
        self._result: Optional[AggregatedShellResultDictType]

    @property
    def _transfer_file_path(self) -> Path:
        return self._cache_path / self.TRANSFER_FILE_NAME

    @property
    def result_file_path(self) -> Path:
        return self._cache_path / self.RESULT_FILE_NAME

    def execute(self) -> None:
        """
        Execution this class would happen in two processes:

        1. The currently running process will serialize itself into disk, and
        executes a helper (worker) script in the background then returns.

        2. The worker script will deserialize the same object from disk, and
        executes the variable status hook inside it, and writes the result to a
        file.
        """

        self._save_to_disk()
        args = [
            str(sys.executable),
            str(self.REFRESH_TASK_SCRIPT_PATH),
            "--transfer-file-path",
            str(self._transfer_file_path),
        ]
        Popen(args)

    def _save_to_disk(self) -> None:
        serialized_data = {
            "task_id": self._task_id,
            "variable_name": self._variable_name,
            "variable_values": self._variable_values,
            "cache_path": str(self._cache_path),
            "variable_status_hook": self._variable_status_hook.serialize(),
        }

        with open(self._transfer_file_path, "w+") as f:
            json.dump(serialized_data, f)

    @staticmethod
    def _load_from_disk(transfer_file_path: Path) -> "VariableStatusRefreshTask":
        with open(transfer_file_path, "r") as f:
            serialized_data = json.load(f)

        variable_status_hook = VariableStatusHook.deserialize(
            serialized_data=serialized_data["variable_status_hook"]
        )
        loaded_object = VariableStatusRefreshTask(
            task_id=serialized_data["task_id"],
            variable_name=serialized_data["variable_name"],
            variable_values=serialized_data["variable_values"],
            cache_path=Path(serialized_data["cache_path"]),
            variable_status_hook=variable_status_hook,
        )

        return loaded_object

    @staticmethod
    def load_and_execute_from_transfer_file(transfer_file_path: Path) -> None:
        refresh_task = VariableStatusRefreshTask._load_from_disk(
            transfer_file_path=transfer_file_path
        )
        refresh_task._execute_in_worker()

    def _execute_in_worker(self) -> None:
        """
        This method will be executed in the worker process.
        """

        result: AggregatedShellResultDictType = {}

        # Execute prepare step if needed
        if self._variable_status_hook.prepare_step_necessary:
            hook_execution_result = self._variable_status_hook.execute_prepare_step(
                variable_name=self._variable_name
            )

        # Execute the processing steps one by one.
        for variable_value in self._variable_values:
            hook_execution_result = self._variable_status_hook.execute_execute_step(
                variable_name=self._variable_name,
                variable_value=variable_value,
            )

            if hook_execution_result.execution_result:
                result[variable_value] = {
                    "processed": hook_execution_result.status_code == 0,
                    "status_string": hook_execution_result.execution_result.stdout[0]
                    if hook_execution_result.execution_result.stdout
                    else "",
                }
            else:
                raise ValueError(
                    f"Variable status hook execution failed: '{hook_execution_result}'"
                )

        with open(self.result_file_path, "w+") as f:
            json.dump(result, f, indent=4)

    @property
    def has_finished(self) -> bool:
        try:
            with open(self.result_file_path) as f:
                self._result = json.load(f)
                return True
        except (FileNotFoundError, ValueError):
            return False

    @property
    def result(self) -> AggregatedVariableStatusesType:
        if self._result is not None:
            partial_aggregated_variable_statuses: AggregatedVariableStatusesType = {
                self._variable_name: {},
            }
            for variable_value, variable_status_result in self._result.items():
                variable_status = VariableStatus(**variable_status_result)
                if variable_status.processed and not variable_status.status_string:
                    variable_status.status_string = "added"
                partial_aggregated_variable_statuses[self._variable_name][
                    variable_value
                ] = variable_status
            return partial_aggregated_variable_statuses
        else:
            raise SystemError("Results call happened on the unfinished status hook!")


class VariableStatusManager:
    """
    Separated manager class that is dedicated to collect and manage the variable statuses.
    """

    def __init__(
        self,
        aggregated_variables: AggregatedVariablesType,
        aggregated_variable_status_hooks: AggregatedVariableStatusHooksType,
        settings: Settings,
    ) -> None:
        self._aggregated_variables = aggregated_variables
        self._aggregated_variable_status_hooks = aggregated_variable_status_hooks
        self._aggregated_variable_statuses = self._initialize_variable_status_statuses(
            aggregated_variables=self._aggregated_variables
        )
        self._settings = settings
        self._running_refresh_tasks: List[VariableStatusRefreshTask] = []

    def _initialize_variable_status_statuses(
        self, aggregated_variables: AggregatedVariablesType
    ) -> AggregatedVariableStatusesType:
        variable_status_dictionary: AggregatedVariableStatusesType = defaultdict(dict)
        for variable_name, variable_values in aggregated_variables.items():
            for variable_value in variable_values:
                variable_status_dictionary[variable_name][
                    variable_value
                ] = VariableStatus(processed=False, status_string="loading")
        return dict(variable_status_dictionary)

    def get(self, variable_name: str, variable_value: str) -> VariableStatus:
        """
        Returns the status of the given variable value defined for a variable
        name.
        """
        for refresh_task in self._running_refresh_tasks:
            if refresh_task.has_finished:
                self._aggregated_variable_statuses.update(refresh_task.result)
        try:
            return self._aggregated_variable_statuses[variable_name][variable_value]
        except KeyError:
            return VariableStatus(processed=False, status_string="disabled")

    def refresh(self, variable_name: str) -> None:
        if variable_name not in self._aggregated_variable_status_hooks:
            # TODO: report a warning about missing variable status hook
            # print(f"missing varibale status hook for variable '{variable_name}'")
            return

        task_id = uuid.uuid4().hex
        task_cache_path = self._settings.dm_cache_variable_status_hooks / task_id
        refresh_task = VariableStatusRefreshTask(
            task_id=task_id,
            variable_name=variable_name,
            variable_values=self._aggregated_variables[variable_name],
            variable_status_hook=self._aggregated_variable_status_hooks[variable_name],
            cache_path=task_cache_path,
        )
        refresh_task.execute()
        self._running_refresh_tasks.append(refresh_task)

    def refresh_all(self) -> None:
        for variable_name in self._aggregated_variables:
            self.refresh(variable_name=variable_name)
