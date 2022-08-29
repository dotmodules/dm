from dataclasses import dataclass
from typing import Dict, List, Optional

from dotmodules.modules.hooks.base import Hook, HookAdapterScript, HookExecutionType
from dotmodules.modules.links import LinkItem
from dotmodules.modules.path import PathManager


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

    links: List[LinkItem]

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
