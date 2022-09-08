from pathlib import Path

from pytest_bdd import given

from dotmodules.settings import Settings

from ..base import p


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


@given(p('I added a directory to "{path:P}"'))
def add_a_directory_to_the_main_modules_directory(
    settings: Settings, path: Path
) -> None:
    absolute_path = settings.relative_modules_path / path
    absolute_path.mkdir(parents=True, exist_ok=True)


def assert_main_modules_directory(settings: Settings) -> None:
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
    assert_main_modules_directory(settings=settings)

    absolute_module_path = settings.relative_modules_path / module_path
    absolute_module_path.mkdir(parents=True, exist_ok=True)

    absolute_config_file_path = absolute_module_path / settings.config_file_name
    absolute_config_file_path.touch()


@given(p('I added a config file to "{module_path:P}" with content:\n{raw_lines:S}'))
def add_config_file_to_module_with_content(
    settings: Settings, module_path: Path, raw_lines: str, tmp_path: Path
) -> None:
    assert_main_modules_directory(settings=settings)

    absolute_module_path = settings.relative_modules_path / module_path
    absolute_module_path.mkdir(parents=True, exist_ok=True)

    absolute_config_file_path = absolute_module_path / settings.config_file_name

    with open(absolute_config_file_path, "w") as f:
        f.write(raw_lines)
