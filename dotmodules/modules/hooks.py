import os
from abc import abstractmethod, abstractproperty
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from dotmodules.modules.modules import Module

from dotmodules.modules.errors import ErrorListProvider
from dotmodules.modules.links import LinkItem
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


class VariableStatusHookExecutionMode(str, Enum):
    PREPARE = "prepare"
    EXECUTE = "execute"


@dataclass
class VariableStatus:
    processed: bool
    status_string: str


@dataclass
class HookExecutionContext:
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


@dataclass
class ShellScriptHook(Hook):
    """
    Specialized hook that can execute an external shell script.
    """

    path_to_script: str
    name: str
    priority: int = 0

    # Abstract Hook base class implementations.
    @property
    def hook_name(self) -> str:
        return self.name

    @property
    def hook_priority(self) -> int:
        return self.priority

    @property
    def hook_description(self) -> str:
        return f"Runs local script <<UNDERLINE>>{self.path_to_script}<<RESET>>"

    @property
    def hook_execution_type(self) -> HookExecutionType:
        return HookExecutionType.INTERACTIVE

    @property
    def hook_adapter_script(self) -> HookAdapterScript:
        return HookAdapterScript.SHELL_SCRIPT

    def get_additional_hook_arguments(
        self,
        path_manager: PathManager,
        extra_arguments: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        # Extra arguments won't be used here as all arguments will be generated
        # from the hook itself.
        return [
            # 9 - dm__config__target_hook_script
            str(path_manager.resolve_local_path(self.path_to_script)),
        ]

    # Abstract ErrorListProvider base class implementations.
    def report_errors(self, path_manager: PathManager) -> List[str]:
        """
        The path to script should be relative to the module root directory.
        """
        errors = []
        full_path = path_manager.resolve_local_path(self.path_to_script)
        if not full_path.is_file():
            message = f"ShellScriptHook[{self.name}]: path_to_script '{self.path_to_script}' does not name a file!"
            errors.append(message)
        return errors


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


@dataclass
class LinkDeploymentHook(Hook):
    """
    Hook that can deploy the given symlinks. This class is only responsible for
    starting the external shell script that will do the actual deployment.
    """

    # Constant values for this class.
    NAME = "DEPLOY_LINKS"

    links: List["LinkItem"]

    # Abstract Hook base class implementations.
    @property
    def hook_name(self) -> str:
        return self.NAME

    @property
    def hook_priority(self) -> int:
        """
        Link deployment hooks has the same priority.
        """
        return 0

    @property
    def hook_description(self) -> str:
        link_count = len(self.links)
        if link_count == 1:
            return f"Deploys {len(self.links)} link"
        else:
            return f"Deploys {len(self.links)} links"

    @property
    def hook_execution_type(self) -> HookExecutionType:
        return HookExecutionType.INTERACTIVE

    @property
    def hook_adapter_script(self) -> HookAdapterScript:
        return HookAdapterScript.LINK_DEPLOYMENT

    def get_additional_hook_arguments(
        self,
        path_manager: PathManager,
        extra_arguments: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        # Extra arguments won't be used here as all arguments will be generated
        # from the hook itself.
        args = []
        for link in self.links:
            # 9..11.. - path_to_target
            args.append(str(path_manager.resolve_local_path(link.path_to_target)))
            # 10..12.. - path_to_symlink
            args.append(str(path_manager.resolve_absolute_path(link.path_to_symlink)))
        return args

    # Abstract ErrorListProvider base class implementations.
    def report_errors(self, path_manager: PathManager) -> List[str]:
        """
        This hook won't report any errors.
        """
        return []


@dataclass
class LinkCleanUpHook(Hook):
    """
    Hook that can clean up the given symlinks. This class is only responsible
    for starting the external shell script that will do the actual clean up.
    """

    NAME = "CLEAN_UP_LINKS"

    links: List["LinkItem"]

    # Abstract Hook base class implementations.
    @property
    def hook_name(self) -> str:
        return self.NAME

    @property
    def hook_priority(self) -> int:
        """
        Link cleanup hooks has the same priority.
        """
        return 0

    @property
    def hook_description(self) -> str:
        link_count = len(self.links)
        if link_count == 1:
            return f"Cleans up {len(self.links)} link"
        else:
            return f"Cleans up {len(self.links)} links"

    @property
    def hook_execution_type(self) -> HookExecutionType:
        return HookExecutionType.INTERACTIVE

    @property
    def hook_adapter_script(self) -> HookAdapterScript:
        return HookAdapterScript.LINK_CLEAN_UP

    def get_additional_hook_arguments(
        self,
        path_manager: PathManager,
        extra_arguments: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        # Extra arguments won't be used here as all arguments will be generated
        # from the hook itself.
        args = []
        for link in self.links:
            # 9..10..11.. - path_to_symlink
            args.append(str(path_manager.resolve_absolute_path(link.path_to_symlink)))
        return args

    # Abstract ErrorListProvider base class implementations.
    def report_errors(self, path_manager: PathManager) -> List[str]:
        """
        This hook won't report any errors.
        """
        return []
