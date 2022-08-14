import json
import sys
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from subprocess import Popen  # nosec
from typing import Dict, List, Optional, TypedDict

from dotmodules.modules.hooks import VariableStatus, VariableStatusHookExecutionMode
from dotmodules.modules.types import (
    AggregatedVariableStatusesType,
    AggregatedVariableStatusHooksType,
    AggregatedVariablesType,
)
from dotmodules.settings import Settings


class ShellResultDict(TypedDict):
    processed: bool
    status_string: str


@dataclass
class VariableStatusRefreshTask:
    REFRESH_TASK_SCRIPT_PATH = Path.cwd() / "dm_variable_status_worker.py"
    TRANSFER_FILE_NAME = "transfer.pickle"
    RESULTS_FILE_NAME = "results.json"

    task_id: str
    cache_path: Path
    target_variables: AggregatedVariablesType
    target_hooks: AggregatedVariableStatusHooksType

    # TODO: create proper type for this
    _results: Optional[Dict[str, Dict[str, ShellResultDict]]] = field(
        init=False, default=None
    )

    @classmethod
    def create(
        cls,
        target_variables: List[str],
        aggregated_variables: AggregatedVariablesType,
        aggregated_variable_status_hooks: AggregatedVariableStatusHooksType,
        variable_status_cache: Path,
    ) -> "VariableStatusRefreshTask":
        # Generating the unique id for the task.
        task_id = uuid.uuid4().hex

        # Creating the cache directory for the task.
        cache_path = variable_status_cache / task_id
        cache_path.mkdir(parents=True)

        # Preparing the hooks and variables.
        scoped_target_variables: AggregatedVariablesType = {}
        scoped_target_hooks: AggregatedVariableStatusHooksType = {}
        for target_variable in target_variables:
            if target_variable in aggregated_variable_status_hooks:
                scoped_target_variables[target_variable] = aggregated_variables[
                    target_variable
                ]
                scoped_target_hooks[target_variable] = aggregated_variable_status_hooks[
                    target_variable
                ]

        return cls(
            task_id=task_id,
            cache_path=cache_path,
            target_variables=scoped_target_variables,
            target_hooks=scoped_target_hooks,
        )

    @property
    def transfer_file_path(self) -> Path:
        return self.cache_path / self.TRANSFER_FILE_NAME

    @property
    def results_file_path(self) -> Path:
        return self.cache_path / self.RESULTS_FILE_NAME

    def _save_to_disk(self) -> None:
        import pickle  # nosec

        with open(self.transfer_file_path, "wb+") as f:
            pickle.dump(self, f)

    @staticmethod
    def _load_from_disk(transfer_file_path: Path) -> "VariableStatusRefreshTask":
        import pickle  # nosec

        with open(transfer_file_path, "rb") as f:
            loaded_object = pickle.load(f)  # nosec
            if not isinstance(loaded_object, VariableStatusRefreshTask):
                raise ValueError("Invalid unpickled object!")

        return loaded_object

    @staticmethod
    def load_and_execute_from_transfer_file(transfer_file_path: Path) -> None:
        refresh_task = VariableStatusRefreshTask._load_from_disk(
            transfer_file_path=transfer_file_path
        )
        refresh_task._execute_in_worker()

    def execute(self) -> None:
        self._save_to_disk()
        args = [
            str(sys.executable),
            str(self.REFRESH_TASK_SCRIPT_PATH),
            "--transfer-file-path",
            str(self.transfer_file_path),
        ]
        Popen(args)

    def _execute_in_worker(self) -> None:
        results: Dict[str, Dict[str, ShellResultDict]] = {}
        for variable_name, variable_values in self.target_variables.items():
            hook = self.target_hooks[variable_name]
            if hook.prepare_step_necessary:
                hook_execution_result = hook.execute(
                    extra_arguments={
                        "execution_mode": VariableStatusHookExecutionMode.PREPARE,
                        "variable_name": variable_name,
                        "variable_value": "",
                    },
                )
            results[variable_name] = {}
            for variable_value in variable_values:
                hook_execution_result = hook.execute(
                    extra_arguments={
                        "execution_mode": VariableStatusHookExecutionMode.EXECUTE,
                        "variable_name": variable_name,
                        "variable_value": variable_value,
                    },
                )
                if hook_execution_result.execution_result:
                    results[variable_name][variable_value] = {
                        "processed": hook_execution_result.status_code == 0,
                        "status_string": hook_execution_result.execution_result.stdout[
                            0
                        ]
                        if hook_execution_result.execution_result.stdout
                        else "",
                    }
                else:
                    raise ValueError(
                        f"Variable status hook execution failed: '{hook_execution_result}'"
                    )

        with open(self.results_file_path, "w+") as f:
            json.dump(results, f, indent=4)

    @property
    def has_finished(self) -> bool:
        try:
            with open(self.results_file_path) as f:
                self._results = json.load(f)
                return True
        except (FileNotFoundError, ValueError):
            return False

    @property
    def results(self) -> AggregatedVariableStatusesType:
        if self._results is not None:
            partial_aggregated_variable_statuses: AggregatedVariableStatusesType = (
                defaultdict(dict)
            )
            for variable_name, variable_value_statuses in self._results.items():
                for variable_value in variable_value_statuses.keys():
                    variable_status_result = variable_value_statuses[variable_value]
                    variable_status = VariableStatus(**variable_status_result)
                    if variable_status.processed and not variable_status.status_string:
                        variable_status.status_string = "added"
                    partial_aggregated_variable_statuses[variable_name][
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
                self._aggregated_variable_statuses.update(refresh_task.results)
        try:
            return self._aggregated_variable_statuses[variable_name][variable_value]
        except KeyError:
            return VariableStatus(processed=False, status_string="disabled")

    def refresh(
        self, variable: Optional[str] = None, variables: Optional[List[str]] = None
    ) -> None:
        if variable and variables:
            raise ValueError("cannot pass both variable and variables at the same time")
        target_variables = []
        if variable:
            target_variables.append(variable)
        if variables:
            target_variables += variables

        refresh_task = VariableStatusRefreshTask.create(
            target_variables=target_variables,
            aggregated_variables=self._aggregated_variables,
            aggregated_variable_status_hooks=self._aggregated_variable_status_hooks,
            variable_status_cache=self._settings.dm_cache_variable_status_hooks,
        )
        refresh_task.execute()
        self._running_refresh_tasks.append(refresh_task)
