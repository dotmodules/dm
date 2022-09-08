import os
from pathlib import Path

from pytest_bdd import given

from dotmodules.settings import Settings

from ..base import p


@given(p('I have the main modules directory at "{relative_modules_path:P}"'))
def set_main_modules_directory(
    settings: Settings, tmp_path: Path, relative_modules_path: Path
) -> None:
    absolute_modules_path = tmp_path / relative_modules_path
    absolute_modules_path.mkdir(parents=True)

    # By default the current working directory is the dm repository root.
    dm_repo_path = Path.cwd()

    # Calculating the relative modules path from the dotmodules repository root
    # to the modules directory. This calculation is done by the dotmodules
    # install script.
    settings.raw_relative_modules_path = Path(
        os.path.relpath(absolute_modules_path, dm_repo_path)
    )


@given(p('I set the dotmodules config file name as "{config_file_name:S}"'))
def set_config_file_name(settings: Settings, config_file_name: str) -> None:
    settings.config_file_name = config_file_name
