from dataclasses import dataclass
from typing import Dict, List, Optional

from dotmodules.modules.hooks.base import Hook, HookAdapterScript, HookExecutionType
from dotmodules.modules.path import PathManager


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
