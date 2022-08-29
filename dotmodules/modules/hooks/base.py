import os
from abc import abstractmethod, abstractproperty
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, TypedDict

if TYPE_CHECKING:
    from dotmodules.modules.modules import Module

from dotmodules.modules.errors import ErrorListProvider
from dotmodules.modules.path import PathManager
from dotmodules.settings import Settings
from dotmodules.shell_adapter import ShellAdapter, ShellResult


class HookError(Exception):
    """
    Exception raised on hook related errors.
    """


class HookAdapterScript(str, Enum):
    """
    Available hook adapter scripts that can be selected by the hooks. The paths
    of the scripts has to be relative to the repository root.
    """

    SHELL_SCRIPT: str = "./utils/hooks/dm_hook__shell_script_adapter.sh"
    LINK_DEPLOYMENT: str = "./utils/hooks/dm_hook__link_deployment_adapter.sh"
    LINK_CLEAN_UP: str = "./utils/hooks/dm_hook__link_clean_up_adapter.sh"
    VARIABLE_STATUS: str = "./utils/hooks/dm_hook__variable_status_adapter.sh"


@dataclass
class HookExecutionResult:
    status_code: int
    execution_result: Optional[ShellResult] = None


class HookExecutionType(str, Enum):
    INTERACTIVE = "interactive"
    CAPTURE = "capture"


@dataclass
class HookExecutionContext:
    module_name: str
    module_root: str
    dm_cache_root: str
    dm_cache_variables: str
    indent: str
    text_wrap_limit: str


class SerializedHookExecutionContextDict(TypedDict):
    module_name: str
    module_root: str
    dm_cache_root: str
    dm_cache_variables: str
    indent: str
    text_wrap_limit: str


@dataclass
class HookExecutionContextMixin:
    """
    This is a workaround mixin, as mypy currently doesn't support abstract dataclasses:
    https://github.com/python/mypy/issues/5374#issuecomment-568335302
    """

    execution_context: HookExecutionContext = field(init=False)

    def initialize_execution_context(
        self, module: "Module", settings: Settings
    ) -> None:
        self.execution_context = HookExecutionContext(
            module_name=str(module.name),
            module_root=str(module.root),
            dm_cache_root=str(settings.dm_cache_root),
            dm_cache_variables=str(settings.dm_cache_variables),
            indent=str(settings.indent),
            text_wrap_limit=str(settings.text_wrap_limit),
        )


class Hook(ErrorListProvider, HookExecutionContextMixin):
    """
    Abstract hook base class that defines the standard hook interface and
    implements the call to the hook adapter scripts.
    """

    @abstractproperty
    def hook_name(self) -> str:
        """
        Property that should return the name of the hook.
        """

    @abstractproperty
    def hook_priority(self) -> int:
        """
        Property that should return the priority of the hook.
        """

    @abstractproperty
    def hook_execution_type(self) -> HookExecutionType:
        """
        Property that should return the execution type of the given hook.
        """

    @abstractproperty
    def hook_description(self) -> str:
        """
        Property that should return a short description about the hook.
        """

    @abstractproperty
    def hook_adapter_script(self) -> HookAdapterScript:
        """
        Property that should return the path of the selected hook adapter
        script. The valid values are present in the HookAdapterScript class.
        """

    @abstractmethod
    def get_additional_hook_arguments(
        self,
        path_manager: PathManager,
        extra_arguments: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """
        Additional arguments that should be handled by the target script
        returned as a list of strings. Extra arguments might be piped from the
        calling process. The implementation should accomodate to this.
        """

    def execute(
        self,
        extra_arguments: Optional[Dict[str, str]] = None,
    ) -> HookExecutionResult:
        """
        Executes the given external hook command.
        """

        if not self.execution_context:
            raise HookError("Execution context was not set up for hook!")

        command = self._assemble_command(
            extra_arguments=extra_arguments,
        )

        adapter = ShellAdapter()

        if self.hook_execution_type == HookExecutionType.INTERACTIVE:
            status_code = adapter.execute_interactively(
                command=command, cwd=Path(self.execution_context.module_root)
            )
            result = HookExecutionResult(status_code=status_code)

        elif self.hook_execution_type == HookExecutionType.CAPTURE:
            shell_result = adapter.execute_and_capture(
                command=command, cwd=Path(self.execution_context.module_root)
            )
            result = HookExecutionResult(
                status_code=shell_result.status_code,
                execution_result=shell_result,
            )

        return result

    def _assemble_command(
        self,
        extra_arguments: Optional[Dict[str, str]] = None,
    ) -> List[str]:

        path_manager = PathManager(root_path=Path(self.execution_context.module_root))

        # Getting the absolute path to the selected hook adapter script. This
        # value will be the 0th parameter for the shell adapter. We are
        # resolving symlinks here to support the use case if the dm repository
        # is in a symlinked path.
        absolute_hook_adapter_script = path_manager.resolve_absolute_path(
            self.hook_adapter_script.value,  # accessing the enum string value
            resolve_symlinks=True,
        )

        # Calculating the relative path from the module's root to the dm
        # repository root which is the current working directory as the hook
        # will be executed from the given module's root directory and the
        # tooling need to reach the repository root from there.
        relative_dm_repo_root = path_manager.get_relative_path(
            from_path=Path(self.execution_context.module_root),
            to_path=os.getcwd(),
        )

        # The adapter scripts require a special set of arguments for the
        # internal common library to function. These arguments are filled by
        # default, sourced from the abstract property implementations. The order
        # of these arguments have to be in sync with the 'dm_hook__common.sh'
        # script!
        command = [
            # 0 - hook adapter script absolute path
            str(absolute_hook_adapter_script),
            # 1 - DM_REPO_ROOT
            str(relative_dm_repo_root),
            # 2 - dm__config__target_hook_name
            str(self.hook_name),
            # 3 - dm__config__target_hook_priority
            str(self.hook_priority),
            # 4 - dm__config__target_module_name
            str(self.execution_context.module_name),
            # 5 - dm__config__dm_cache_root
            str(self.execution_context.dm_cache_root),
            # 6 - dm__config__dm_cache_variables
            str(self.execution_context.dm_cache_variables),
            # 7 - dm__config__indent
            str(self.execution_context.indent),
            # 8 - dm__config__wrap_limit
            str(self.execution_context.text_wrap_limit),
        ]

        # Appending the additional arguments provided by the sub-class.
        command += self.get_additional_hook_arguments(
            path_manager=path_manager, extra_arguments=extra_arguments
        )

        return command
