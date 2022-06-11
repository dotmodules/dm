import os
from abc import abstractmethod, abstractproperty
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List

from dotmodules.modules.errors import ErrorListProvider
from dotmodules.modules.links import LinkItem
from dotmodules.modules.path import PathManager
from dotmodules.settings import Settings
from dotmodules.shell_adapter import ShellAdapter


class HookAdapterScript(str, Enum):
    """
    Available hook adapter scripts that can be selected by the hooks. The paths
    of the scripts has to be relative to the repository root.
    """

    SHELL_SCRIPT: str = "./utils/dm_hook__shell_script_adapter.sh"
    LINK_DEPLOYMENT: str = "./utils/dm_hook__link_deployment_adapter.sh"
    LINK_CLEAN_UP: str = "./utils/dm_hook__link_clean_up_adapter.sh"


class Hook(ErrorListProvider):
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
    def get_additional_hook_arguments(self, path_manager: PathManager) -> List[str]:
        """
        Additional arguments that should be handled by the target script
        returned as a list of strings.
        """

    def _assemble_command(
        self,
        module_name: str,
        module_root: Path,
        path_manager: PathManager,
        settings: Settings,
    ) -> List[str]:
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
            from_path=module_root,
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
            self.hook_name,
            # 3 - dm__config__target_hook_priority
            str(self.hook_priority),
            # 4 - dm__config__target_module_name
            module_name,
            # 5 - dm__config__dm_cache_root
            str(settings.dm_cache_root),
            # 6 - dm__config__dm_cache_variables
            str(settings.dm_cache_variables),
            # 7 - dm__config__indent
            str(settings.indent),
            # 8 - dm__config__wrap_limit
            str(settings.text_wrap_limit),
        ]

        # Appending the additional parameters provided by the sub-class.
        command += self.get_additional_hook_arguments(path_manager=path_manager)

        return command

    def execute(
        self,
        module_name: str,
        module_root: Path,
        path_manager: PathManager,
        settings: Settings,
    ) -> int:
        """
        Executes the given external hook command.
        """
        command = self._assemble_command(
            module_name=module_name,
            module_root=module_root,
            path_manager=path_manager,
            settings=settings,
        )

        adapter = ShellAdapter()
        status_code = adapter.execute_interactively(command=command, cwd=module_root)

        return status_code


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
    def hook_adapter_script(self) -> HookAdapterScript:
        return HookAdapterScript.SHELL_SCRIPT

    def get_additional_hook_arguments(self, path_manager: PathManager) -> List[str]:
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
            message = f"Hook[{self.name}]: path_to_script '{self.path_to_script}' does not name a file!"
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
    def hook_adapter_script(self) -> HookAdapterScript:
        return HookAdapterScript.LINK_DEPLOYMENT

    def get_additional_hook_arguments(self, path_manager: PathManager) -> List[str]:
        args = []
        for link in self.links:
            # 9..11.. - path_to_file
            args.append(str(path_manager.resolve_local_path(link.path_to_file)))
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
    def hook_adapter_script(self) -> HookAdapterScript:
        return HookAdapterScript.LINK_CLEAN_UP

    def get_additional_hook_arguments(self, path_manager: PathManager) -> List[str]:
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
