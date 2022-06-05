from dataclasses import dataclass
from pathlib import Path
from typing import List


class LinkError(Exception):
    pass


@dataclass
class LinkItem:
    path_to_file: str
    path_to_symlink: str
    name: str = "link"

    @property
    def full_path_to_symlink(self) -> Path:
        """
        The path to symlink should be an absolute path with the the option to
        resolve the '$HOME' variable to the users home directory.
        """

    @property
    def link_exists(self) -> bool:
        return self.full_path_to_symlink.is_symlink()

    @property
    def target_matched(self) -> bool:
        return (
            self.link_exists
            and self.full_path_to_symlink.resolve() == self.full_path_to_file
        )

    @property
    def deployed(self) -> bool:
        return self.link_exists and self.target_matched

    def validate(self) -> List[str]:
        errors = []
        try:
            self.full_path_to_file
        except ValueError as e:
            errors.append(str(e))
        try:
            self.full_path_to_symlink
        except ValueError as e:
            errors.append(str(e))

        return errors
        # """
        # The path to file should be relative to the module root directory.
        # """

        # full_path = self.module_root / self.path_to_file
        # if not full_path.is_file():
        #     raise LinkError(
        #         f"Link[{self.name}]: path_to_file '{self.path_to_file}' does not name a file!"
        #     )
        # return full_path
