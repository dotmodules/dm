from pathlib import Path
from typing import Callable, List, Optional, cast

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.hooks import (  # HookExecutionResult,
    ShellScriptHook,
    VariableStatusHook,
)
from dotmodules.modules.links import LinkItem
from dotmodules.modules.modules import Module, ModuleError, Modules
from dotmodules.settings import Settings

# from dotmodules.shell_adapter import ShellResult


@pytest.fixture
def modules(mocker: MockerFixture) -> Modules:
    mock_modules = mocker.MagicMock()
    return cast(Modules, mock_modules)


@pytest.fixture
def module_factory(modules: Modules) -> Callable[..., List[Module]]:
    """
    Module generator factory fixture that can generate a list of module objects
    with indexed generic values. There is also an option to disable specific
    modules by index.
    """

    def factory(
        count: int, disabled_module_indexes: Optional[List[int]] = None
    ) -> List[Module]:

        if not disabled_module_indexes:
            disabled_module_indexes = []

        module_objetcs = []

        for index in range(1, count + 1):
            enabled = index not in disabled_module_indexes

            module = Module(
                name=f"module_{index}",
                version=f"v{index}",
                enabled=enabled,
                documentation=[f"doc_{index}"],
                aggregated_variables={
                    f"var_{index}": [f"value_{index}"],
                    "common": [f"common_{index}"],
                },
                root=Path(f"/module/root/{index}"),
                links=[
                    LinkItem(
                        name=f"link_{index}",
                        path_to_target=f"/path/to/file/{index}",
                        path_to_symlink=f"/path/to/symlink/{index}",
                    ),
                ],
                hooks=[
                    ShellScriptHook(
                        name=f"HOOK_{index}",
                        path_to_script=f"/path/to/script_{index}",
                        priority=index,
                    ),
                    ShellScriptHook(
                        name="COMMON_HOOK",
                        path_to_script=f"/path/to/common_script_{index}",
                        priority=index,
                    ),
                ],
                variable_status_hooks=[
                    VariableStatusHook(
                        path_to_script=f"/path/to/script_{index}",
                        variable_name=f"VARIABLE_NAME_{index}",
                    ),
                ],
                modules=modules,
            )
            module_objetcs.append(module)

        return module_objetcs

    return factory


class TestVariableAggregationCases:
    def test__variables_can_be_aggregated(
        self, module_factory: Callable[..., List[Module]]
    ) -> None:
        module_objects = module_factory(count=6)
        expected = {
            "var_1": ["value_1"],
            "var_2": ["value_2"],
            "var_3": ["value_3"],
            "var_4": ["value_4"],
            "var_5": ["value_5"],
            "var_6": ["value_6"],
            "common": [
                "common_1",
                "common_2",
                "common_3",
                "common_4",
                "common_5",
                "common_6",
            ],
        }
        result = Modules._aggregate_variables(module_objects=module_objects)
        assert result == expected

    def test__variables_gets_aggregated_only_for_enabled_modules(
        self, module_factory: Callable[..., List[Module]]
    ) -> None:
        module_objects = module_factory(count=6, disabled_module_indexes=[3, 6])
        expected = {
            "var_1": ["value_1"],
            "var_2": ["value_2"],
            "var_4": ["value_4"],
            "var_5": ["value_5"],
            "common": [
                "common_1",
                "common_2",
                "common_4",
                "common_5",
            ],
        }
        result = Modules._aggregate_variables(module_objects=module_objects)
        assert result == expected

    def test__variables_are_deduplicated(
        self, module_factory: Callable[..., List[Module]]
    ) -> None:
        module_objects = module_factory(count=6)

        # Setting all the common variables the same for each modules and
        # duplicating all module related varibales.
        for index, module_object in enumerate(module_objects, start=1):
            module_object.aggregated_variables["common"] = ["common"]
            module_object.aggregated_variables[f"var_{index}"] *= 2

        expected = {
            "var_1": ["value_1"],
            "var_2": ["value_2"],
            "var_3": ["value_3"],
            "var_4": ["value_4"],
            "var_5": ["value_5"],
            "var_6": ["value_6"],
            "common": [
                "common",
            ],
        }
        result = Modules._aggregate_variables(module_objects=module_objects)
        assert result == expected


@pytest.fixture
def settings() -> Settings:
    settings = Settings()
    settings.dm_cache_root = Path("/my/dm/cache/root")
    settings.dm_cache_variables = Path("/my/dm/cache/variables")
    settings.indent = "my_indent"
    settings.text_wrap_limit = 42
    return settings


class TestHookAggregationCases:
    def test__hooks_can_be_aggregated(
        self,
        module_factory: Callable[..., List[Module]],
        settings: Settings,
    ) -> None:
        module_objects = module_factory(count=6, disabled_module_indexes=[6])

        expected = {
            "COMMON_HOOK": [
                # The second hook is the common hook in the modules hooks, the
                # lower indexed module has the higher priority.
                module_objects[0].hooks[1],
                module_objects[1].hooks[1],
                module_objects[2].hooks[1],
                module_objects[3].hooks[1],
                module_objects[4].hooks[1],
            ],
            "HOOK_1": [
                module_objects[0].hooks[0],
            ],
            "HOOK_2": [
                module_objects[1].hooks[0],
            ],
            "HOOK_3": [
                module_objects[2].hooks[0],
            ],
            "HOOK_4": [
                module_objects[3].hooks[0],
            ],
            "HOOK_5": [
                module_objects[4].hooks[0],
            ],
        }
        result = Modules._aggregate_hooks(
            module_objects=module_objects, settings=settings
        )
        assert result == expected


class TestVariableStatusHookAggregationCases:
    def test__variable_status_hooks_can_be_aggregated(
        self,
        module_factory: Callable[..., List[Module]],
        settings: Settings,
    ) -> None:
        module_objects = module_factory(count=6, disabled_module_indexes=[6])
        expected = {
            "VARIABLE_NAME_1": module_objects[0].variable_status_hooks[0],
            "VARIABLE_NAME_2": module_objects[1].variable_status_hooks[0],
            "VARIABLE_NAME_3": module_objects[2].variable_status_hooks[0],
            "VARIABLE_NAME_4": module_objects[3].variable_status_hooks[0],
            "VARIABLE_NAME_5": module_objects[4].variable_status_hooks[0],
        }
        result = Modules._aggregate_variable_status_hooks(
            module_objects=module_objects, settings=settings
        )
        assert result == expected

        hook = module_objects[0].variable_status_hooks[0]
        assert hook.execution_context
        assert hook.execution_context.module_name == "module_1"
        assert hook.execution_context.module_root == "/module/root/1"
        assert hook.execution_context.dm_cache_root == "/my/dm/cache/root"
        assert hook.execution_context.dm_cache_variables == "/my/dm/cache/variables"
        assert hook.execution_context.indent == "my_indent"
        assert hook.execution_context.text_wrap_limit == "42"

        hook = module_objects[1].variable_status_hooks[0]
        assert hook.execution_context
        assert hook.execution_context.module_name == "module_2"
        assert hook.execution_context.module_root == "/module/root/2"
        assert hook.execution_context.dm_cache_root == "/my/dm/cache/root"
        assert hook.execution_context.dm_cache_variables == "/my/dm/cache/variables"
        assert hook.execution_context.indent == "my_indent"
        assert hook.execution_context.text_wrap_limit == "42"

        hook = module_objects[2].variable_status_hooks[0]
        assert hook.execution_context
        assert hook.execution_context.module_name == "module_3"
        assert hook.execution_context.module_root == "/module/root/3"
        assert hook.execution_context.dm_cache_root == "/my/dm/cache/root"
        assert hook.execution_context.dm_cache_variables == "/my/dm/cache/variables"
        assert hook.execution_context.indent == "my_indent"
        assert hook.execution_context.text_wrap_limit == "42"

        hook = module_objects[3].variable_status_hooks[0]
        assert hook.execution_context
        assert hook.execution_context.module_name == "module_4"
        assert hook.execution_context.module_root == "/module/root/4"
        assert hook.execution_context.dm_cache_root == "/my/dm/cache/root"
        assert hook.execution_context.dm_cache_variables == "/my/dm/cache/variables"
        assert hook.execution_context.indent == "my_indent"
        assert hook.execution_context.text_wrap_limit == "42"

        hook = module_objects[4].variable_status_hooks[0]
        assert hook.execution_context
        assert hook.execution_context.module_name == "module_5"
        assert hook.execution_context.module_root == "/module/root/5"
        assert hook.execution_context.dm_cache_root == "/my/dm/cache/root"
        assert hook.execution_context.dm_cache_variables == "/my/dm/cache/variables"
        assert hook.execution_context.indent == "my_indent"
        assert hook.execution_context.text_wrap_limit == "42"

    def test__multiple_status_hooks_for_variable__error(
        self,
        module_factory: Callable[..., List[Module]],
        settings: Settings,
    ) -> None:
        module_objects = module_factory(count=6, disabled_module_indexes=[6])

        # Adding another variable status hook for the same variable.
        module_objects[0].variable_status_hooks.append(
            VariableStatusHook(
                path_to_script="/path/to/script_1",
                variable_name="VARIABLE_NAME_2",
            )
        )
        with pytest.raises(ModuleError) as exception_info:
            Modules._aggregate_variable_status_hooks(
                module_objects=module_objects, settings=settings
            )

        expected_error_message = (
            "Multiple varible status hooks were defined for variable "
            "name 'VARIABLE_NAME_2'!"
        )
        assert exception_info.match(expected_error_message)


# @pytest.mark.skip
# class TestModulesVariableStatusRetrievingCases:
#     def test__variable_status_can_be_retrieved(
#         self,
#         mocker: MockerFixture,
#         module_factory: Callable[..., List[Module]],
#         settings: Settings,
#     ) -> None:
#         modules = Modules(settings=settings)
#         module_objects = module_factory(count=2)
#         modules.modules = module_objects
#         modules._variable_status_hooks = {
#             "VARIABLE_NAME_1": HookAggregate(
#                 module=module_objects[0],
#                 hook=VariableStatusHook(
#                     path_to_script="/path/to/script_1",
#                     variable_name="VARIABLE_NAME_1",
#                 ),
#             ),
#             "VARIABLE_NAME_2": HookAggregate(
#                 module=module_objects[1],
#                 hook=VariableStatusHook(
#                     path_to_script="/path/to/script_2",
#                     variable_name="VARIABLE_NAME_2",
#                 ),
#             ),
#         }

#         mock_execute = mocker.patch("dotmodules.modules.hooks.Hook.execute")
#         dummy_variable_status = "dummy_variable_status"
#         mock_execute.return_value = HookExecutionResult(
#             status_code=0,
#             execution_result=ShellResult(
#                 command="dummy_command",
#                 cwd=None,
#                 status_code=0,
#                 stdout=[dummy_variable_status],
#                 stderr=[],
#             ),
#         )

#         result = modules.get_variable_status(
#             variable_name="VARIABLE_NAME_1", variable_value="my_value"
#         )

#         assert result == dummy_variable_status

#         dummy_path_manager = PathManager(root_path=module_objects[0].root)

#         mock_execute.assert_called_once_with(
#             module_name=module_objects[0].name,
#             module_root=module_objects[0].root,
#             path_manager=dummy_path_manager,
#             settings=settings,
#         )

#     def test__execute_variable_status_hook(self, mocker: MockerFixture) -> None:
#         pass
