import json
import os
from pathlib import Path

from pytest_bdd import given, scenarios, then, when

from dotmodules.modules.modules import Modules
from dotmodules.settings import Settings

from .utils import ExecutionContext, FailedContext, ScenarioError, SucceededContext, p

scenarios("../features")

# ============================================================================
#  GIVEN - SETUP - FILES
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
#  GIVEN - SETUP - DIRECTORIES
# ============================================================================


@given(p('I added a directory to "{path:P}"'))
def add_a_directory_to_the_main_modules_directory(
    settings: Settings, path: Path
) -> None:
    absolute_path = settings.relative_modules_path / path
    absolute_path.mkdir(parents=True, exist_ok=True)


# ============================================================================
#  GIVEN - SETUP - SETTINGS
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


@given(p('I am using the "{deployment_target_name:S}" deployment target'))
def set_deployment_target(settings: Settings, deployment_target_name: str) -> None:
    settings.deployment_target = deployment_target_name


@given(p("I am using the default deployment target"))
def set_default_deployment_target(settings: Settings) -> None:
    settings.deployment_target = settings.default_deployment_target


# ============================================================================
#  GIVEN - SETUP - MODULE CONFIG FILE
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
    settings: Settings, module_path: Path, raw_lines: str
) -> None:
    _assert_main_modules_directory(settings=settings)

    absolute_module_path = settings.relative_modules_path / module_path
    absolute_module_path.mkdir(parents=True, exist_ok=True)

    absolute_config_file_path = absolute_module_path / settings.config_file_name

    with open(absolute_config_file_path, "w") as f:
        f.write(raw_lines)


# ============================================================================
#  THEN - MODULE PARAMETERS - DOCUMENTATION
# ============================================================================


@then(p('the module at index "{index:I}" should have empty documentation'))
def assert_module_has_empty_documentation(
    context: ExecutionContext, index: int
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.documentation == []


@then(
    p(
        'the module at index "{index:I}" should have its documentation set to:\n{lines:S}'
    )
)
def assert_module_has_documentation_lines(
    context: ExecutionContext, index: int, lines: str
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert "\n".join(module.documentation) == lines


# ============================================================================
#  THEN - MODULE PARAMETERS - ENABLED
# ============================================================================


@then(p('the module at index "{index:I}" should be enabled'))
def assert_module_enabled_at_index(context: ExecutionContext, index: int) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.enabled is True


@then(p('the module at index "{index:I}" should be disabled'))
def assert_module_disabled_at_index(context: ExecutionContext, index: int) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.enabled is False


# ============================================================================
#  THEN - MODULE PARAMETERS - LINKS
# ============================================================================


@then(p('the module at index "{index:I}" should have "{count:I}" link registered'))
@then(p('the module at index "{index:I}" should have "{count:I}" links registered'))
def assert_module_has_link_count(
    context: ExecutionContext, index: int, count: int
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert len(module.links) == count


# TEHN - NAME
@then(p('the module at index "{index:I}" should have its name set to "{name:S}"'))
def assert_module_name_at_index(
    context: ExecutionContext, index: int, name: str
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.name == name


# THEN - VARIABLES
@then(p('the module at index "{index:I}" should have no variables'))
def assert_module_has_no_varibales(context: ExecutionContext, index: int) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.variables == {}


@then(
    p(
        'the module at index "{index:I}" should have the following variables:\n{json_lines:S}'
    )
)
def assert_module_has_specified_variables(
    context: ExecutionContext, index: int, json_lines: str
) -> None:
    variables = json.loads(json_lines)

    modules = context.modules
    module = modules[index - 1]
    assert module.variables == variables


# ============================================================================
#  THEN - MODULE PARAMETERS - VERSION
# ============================================================================


@then(p('the module at index "{index:I}" should have its version set to "{version:S}"'))
def assert_module_version_at_index(
    context: ExecutionContext, index: int, version: str
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert module.version == version


# ============================================================================
#  THEN - MODULE PARAMETERS - MODULES
# ============================================================================

#  LOADED MODULES
@then("there should be no modules loaded")
@then("there should be no loaded modules")
def no_loaded_modules(context: ExecutionContext) -> None:
    # If the modules object was created check if there are 0 modules loaded.
    if context.succeeded:
        assert len(context.modules) == 0


@then(p('there should be "{count:I}" loaded module'))
@then(p('there should be "{count:I}" loaded modules'))
def count_loaded_modules(context: ExecutionContext, count: int) -> None:
    if count < 1:
        raise ScenarioError("You can only check if there is at least one loaded module")

    modules = context.modules
    assert len(modules) == count


#  MODULE ROOTS
@then(p("the modules should have the following relative roots:\n{roots:S}"))
def assert_module_roots(context: ExecutionContext, roots: str, tmp_path: Path) -> None:
    root_items = roots.splitlines()
    if len(root_items) != len(set(root_items)):
        raise ScenarioError("Given roots should be unique!")

    modules = context.modules
    assert len(modules) == len(root_items)

    module_absolute_roots = [module.root for module in modules]

    for relative_root in root_items:
        absolute_root = tmp_path / relative_root
        assert absolute_root in module_absolute_roots


@then(p("the modules should have the following relative roots in order:\n{roots:S}"))
def assert_module_roots_in_order(
    context: ExecutionContext, roots: str, tmp_path: Path
) -> None:
    root_items = roots.splitlines()
    if len(root_items) != len(set(root_items)):
        raise ScenarioError("Given roots should be unique!")

    modules = context.modules
    assert len(modules) == len(root_items)

    module_absolute_roots = [module.root for module in modules]

    for module_absolute_root, relative_root in zip(module_absolute_roots, root_items):
        absolute_root = tmp_path / relative_root
        assert absolute_root == module_absolute_root


#  GLOBAL ERRORS AND WARNINGS
@then(p("a global error should have been raised:\n{error_message:S}"))
def global_error_should_have_been_raised(
    context: ExecutionContext, error_message: str
) -> None:
    context.match_global_error_message(error_message=error_message)


#  MODULE LEVEL ERRORS AND WARNINGS
@then("there should be no module level errors")
def assert_no_module_level_errors(context: ExecutionContext) -> None:
    modules = context.modules
    for module in modules:
        assert not module.errors


@then(p('there should be no module level errors for module at index "{index:I}"'))
def assert_no_module_level_errors_for_module_at_index(
    context: ExecutionContext, index: int
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert not module.errors


@then(
    p('there should be a module level error for module at index "{index:I}":\n{errors}')
)
@then(
    p('there should be module level errors for module at index "{index:I}":\n{errors}')
)
def assert_module_level_errors_for_module_at_index(
    context: ExecutionContext, index: int, errors: str
) -> None:
    error_list = errors.splitlines()

    modules = context.modules
    module = modules[index - 1]
    for error in error_list:
        assert error in module.errors


@then("there should be no module level warnings")
def assert_no_module_level_warnings(context: ExecutionContext) -> None:
    modules = context.modules
    for module in modules:
        assert not module.warnings


@then(p('there should be no module level warnings for module at index "{index:I}"'))
def assert_no_module_level_warnings_for_module_at_index(
    context: ExecutionContext, index: int
) -> None:
    modules = context.modules
    module = modules[index - 1]
    assert not module.warnings


@then(
    p(
        'there should be a module level warning for module at index "{index:I}":\n{errors}'
    )
)
@then(
    p(
        'there should be module level warnings for module at index "{index:I}":\n{errors}'
    )
)
def assert_module_level_warnings_for_module_at_index(
    context: ExecutionContext, index: int, errors: str
) -> None:
    error_list = errors.splitlines()

    modules = context.modules
    module = modules[index - 1]
    for error in error_list:
        assert error in module.warnings


# ============================================================================
# WHEN - EXWCUTION - SYSTEM LOADING
# ============================================================================


@when("I run the dotmodules system", target_fixture="context")
def load_the_dotmodules_system(settings: Settings) -> ExecutionContext:
    try:
        modules = Modules(settings=settings)
        return SucceededContext(modules=modules)
    except Exception as e:
        return FailedContext(exception=e)
