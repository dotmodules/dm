import os
from pathlib import Path

from pytest_bdd import given, then, when

from dotmodules.modules.modules import Modules
from dotmodules.settings import Settings

from ..base import ExecutionContext, ScenarioError, p, settings


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
    settings.relative_modules_path = Path(
        os.path.relpath(absolute_modules_path, dm_repo_path)
    )


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


@given(p('I set the dotmodules config file name as "{config_file_name:S}"'))
def set_config_file_name(settings: Settings, config_file_name: str) -> None:
    settings.config_file_name = config_file_name


@when("I run the dotmodules system", target_fixture="execution_context")
def load_the_dotmodules_system(settings: Settings) -> ExecutionContext:
    try:
        modules = Modules(settings=settings)
        return ExecutionContext(modules=modules)
    except Exception as e:
        return ExecutionContext(exception=e)


@then("there should be no modules loaded")
@then("there should be no loaded modules")
def no_loaded_modules(execution_context: ExecutionContext) -> None:
    # If the modules object was created check if there are 0 modules loaded.
    if execution_context._modules is not None:
        assert len(execution_context.modules) == 0
    else:
        assert execution_context._modules is None


@then(p('there should be "{count:I}" loaded module'))
@then(p('there should be "{count:I}" loaded modules'))
def count_loaded_modules(execution_context: ExecutionContext, count: int) -> None:
    if count < 1:
        raise ScenarioError("You can only check if there is at least one loaded module")

    modules = execution_context.modules
    assert len(modules) == count


@then(p("a global error should have been raised:\n{error_message:S}"))
def global_error_should_have_been_raised(
    execution_context: ExecutionContext, error_message: str
) -> None:
    execution_context.match_error_message(error_message=error_message)
