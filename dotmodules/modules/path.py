import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PathManager:
    """
    Utility class that can be used to path related operations. It can resolve
    local files relative to the rooth_path passed to the class at instantiation.
    It can resolve absolute partial absolute paths, while resolving the '$HOME'
    literal in them. It can also calculate the relative path between two given
    paths.
    """

    HOME_LITERAL__STANDARD = "$HOME"
    HOME_LITERAL__GUARDED = "${HOME}"

    root_path: Path

    def resolve_local_path(self, local_path: str | Path) -> Path:
        """
        Resolves module local path that is relative to the root path into an
        absolute path.
        """
        local_path = Path(local_path)
        return self.root_path / local_path

    def resolve_absolute_path(
        self, absolute_path: str | Path, resolve_symlinks: bool = False
    ) -> Path:
        """
        Resolves an absolute path by replacing the optional '$HOME' literal into
        the users home directory. Partial paths will be assumed to originated
        from the current working directory and will be resolved as an absolute
        path.

        By default it won't resolve symbolic links, but there is an option to do
        that if it is necessary.
        """
        home_directory = str(Path.home())
        absolute_path = str(absolute_path)
        absolute_path = absolute_path.replace(
            self.HOME_LITERAL__STANDARD, home_directory
        )
        absolute_path = absolute_path.replace(
            self.HOME_LITERAL__GUARDED, home_directory
        )
        if resolve_symlinks:
            return Path(absolute_path).resolve()
        else:
            absolute_path = os.path.abspath(absolute_path)
            return Path(absolute_path)

    def get_relative_path(self, from_path: str | Path, to_path: str | Path) -> Path:
        """
        Calculates the relative path from the from_path to the to_path.

        Example 1
        -----------------------------------------------------------------------
        from_path: ./dir_1
        to_path: ./dir_1/dir_2/dir_3
        result: dir_2/dir_3

        Example 2
        -----------------------------------------------------------------------
        from_path: ./dir_1/dir_2/dir_3
        to_path: ./dir_1
        result: ../..
        """
        return Path(os.path.relpath(to_path, from_path))
