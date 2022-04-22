from pathlib import Path
from typing import List

import pytest

from dotmodules.modules import HookItem, LinkItem, Module, Modules


@pytest.fixture
def module_factory():
    def factory(count: int) -> List[Module]:
        module_objetcs = []
        for index in range(1, count + 1):
            module = Module(
                name=f"module_{index}",
                version=f"v{index}",
                documentation=[f"doc_{index}"],
                variables={
                    f"var_{index}": [f"value_{index}"],
                    "common": [f"common_{index}"],
                },
                links=[
                    LinkItem(
                        name=f"link_{index}",
                        path_to_file=f"/path/to/file/{index}",
                        path_to_symlink=f"/path/to/symlink/{index}",
                    )
                ],
                hooks=[
                    HookItem(
                        name=f"HOOK_{index}",
                        path_to_script=f"/path/to/script_{index}",
                        priority=index,
                    ),
                    HookItem(
                        name="COMMON_HOOK",
                        path_to_script=f"/path/to/common_script_{index}",
                        priority=index,
                    ),
                ],
                root=Path(f"/module/root/{index}"),
            )
            module_objetcs.append(module)
        return module_objetcs

    return factory


@pytest.fixture
def modules(module_factory):
    module_objects = module_factory(count=5)
    modules = Modules()
    modules.modules = module_objects
    return modules


class TestModuleAggregationCases:
    def test__variables_can_be_aggregated(self, modules):
        result = modules.variables
        expected = {
            "var_1": ["value_1"],
            "var_2": ["value_2"],
            "var_3": ["value_3"],
            "var_4": ["value_4"],
            "var_5": ["value_5"],
            "common": [
                "common_1",
                "common_2",
                "common_3",
                "common_4",
                "common_5",
            ],
        }

        assert result == expected

    def test__hooks_can_be_aggregated(self, modules):
        result = modules.hooks
        expected = {
            "COMMON_HOOK": [
                # The second hook is the common hook in the modules hooks, the
                # lower indexed module has the higher priority.
                modules.modules[0].hooks[1],
                modules.modules[1].hooks[1],
                modules.modules[2].hooks[1],
                modules.modules[3].hooks[1],
                modules.modules[4].hooks[1],
            ],
            "HOOK_1": [modules.modules[0].hooks[0]],
            "HOOK_2": [modules.modules[1].hooks[0]],
            "HOOK_3": [modules.modules[2].hooks[0]],
            "HOOK_4": [modules.modules[3].hooks[0]],
            "HOOK_5": [modules.modules[4].hooks[0]],
        }

        assert result == expected
