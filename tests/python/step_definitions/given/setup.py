import os
from pathlib import Path

from pytest_bdd import given

from dotmodules.settings import Settings

from ..base import p

# ============================================================================
#  FILES
# ============================================================================


@given(p('I added an empty file to "{path:P}"'))
def add_an_empty_file_to_the_main_modules_directory(
    settings: Settings, path: Path
) -> None:
    absolute_path = settings.relative_modules_path / path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    absolute_path.touch()


@given(p('I added a file to "{path:P}" with content:\n{raw_lines:S}'))
def add_a_file_to_the_main_modules_directory_with_content(
    settings: Settings, path: Path, raw_lines: str
) -> None:
    absolute_path = settings.relative_modules_path / path
    absolute_path.parent.mkdir(parents=True, exist_ok=True)
    with open(absolute_path, "w") as f:
        f.write(raw_lines)


# ============================================================================
#  DIRECTORIES
# ============================================================================


@given(p('I added a directory to "{path:P}"'))
def add_a_directory_to_the_main_modules_directory(
    settings: Settings, path: Path
) -> None:
    absolute_path = settings.relative_modules_path / path
    absolute_path.mkdir(parents=True, exist_ok=True)


# ============================================================================
#  SETTINGS
# ============================================================================


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


# ============================================================================
#  MODULE CONFIG FILE
# ============================================================================


def _assert_main_modules_directory(settings: Settings) -> None:
    if (
        not settings.relative_modules_path
        or not settings.relative_modules_path.is_dir()
    ):
        message = "You need to set up the main modules directory before you can add a config file."
        if settings.relative_modules_path:
            message += (
                " The relative path to the main modules directory is currently set to "
                f"'{settings.relative_modules_path}'"
            )
        raise SystemError(message)


@given(p('I added an empty config file to "{module_path:P}"'))
def add_empty_config_file_to_module(settings: Settings, module_path: Path) -> None:
    _assert_main_modules_directory(settings=settings)

    absolute_module_path = settings.relative_modules_path / module_path
    absolute_module_path.mkdir(parents=True, exist_ok=True)

    absolute_config_file_path = absolute_module_path / settings.config_file_name
    absolute_config_file_path.touch()


@given(p('I added a config file to "{module_path:P}" with content:\n{raw_lines:S}'))
def add_config_file_to_module_with_content(
    settings: Settings, module_path: Path, raw_lines: str, tmp_path: Path
) -> None:
    _assert_main_modules_directory(settings=settings)

    absolute_module_path = settings.relative_modules_path / module_path
    absolute_module_path.mkdir(parents=True, exist_ok=True)

    absolute_config_file_path = absolute_module_path / settings.config_file_name

    with open(absolute_config_file_path, "w") as f:
        f.write(raw_lines)
