from dataclasses import dataclass
from typing import List

from dotmodules.modules.errors import ErrorListProvider
from dotmodules.modules.path import PathManager


@dataclass
class LinkItem(ErrorListProvider):
    path_to_target: str
    path_to_symlink: str
    name: str = "link"

    def check_if_link_exists(self, path_manager: PathManager) -> bool:
        full_path_to_symlink = path_manager.resolve_absolute_path(self.path_to_symlink)
        return full_path_to_symlink.is_symlink()

    def check_if_target_matched(self, path_manager: PathManager) -> bool:
        """
        Checks if the given link exists and its target matches the given file.
        """
        full_path_to_target = path_manager.resolve_local_path(self.path_to_target)
        full_path_to_symlink = path_manager.resolve_absolute_path(self.path_to_symlink)
        return (
            full_path_to_symlink.is_symlink()
            and full_path_to_symlink.resolve() == full_path_to_target
        )

    # Abstract ErrorListProvider base class implementations.
    def report_errors(self, path_manager: PathManager) -> List[str]:
        errors = []

        full_path_to_target = path_manager.resolve_local_path(self.path_to_target)

        if not full_path_to_target.is_file() and not full_path_to_target.is_dir():
            message = f"Link[{self.name}]: path_to_target '{self.path_to_target}' does not name a file or directory!"
            errors.append(message)

        return errors
