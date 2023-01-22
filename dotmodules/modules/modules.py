import re
import shutil
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterator, List, Sequence, Union

from dotmodules.modules.hooks import (Hook, LinkCleanUpHook,
                                      LinkDeploymentHook, ShellScriptHook,
                                      VariableStatusHook)
from dotmodules.modules.links import LinkItem
from dotmodules.modules.loader import ConfigLoader, LoaderError
from dotmodules.modules.parser import (ConfigParser, LinkItemDict, ParserError,
                                       ShellScriptHookItemDict,
                                       VariableStatusHookItemDict)
from dotmodules.modules.path import PathManager
from dotmodules.modules.types import (AggregatedHooksType,
                                      AggregatedVariableStatusHooksType,
                                      AggregatedVariablesType)
from dotmodules.modules.variable_status import VariableStatusManager
from dotmodules.settings import Settings


class ModuleError(Exception):
    """
    Exception that will be raised on module level errors.
    """


class ModuleStatus(str, Enum):
    DISABLED: str = "disabled"
    DEPLOYED: str = "deployed"
    INCOMPLETE: str = "incomplete"
    ERROR: str = "error"
    LOADING: str = "loading"


@dataclass
class Module:
    root: Path
    name: str
    version: str
    enabled: bool
    documentation: Sequence[str]
    variables: AggregatedVariablesType
    links: Sequence[LinkItem]
    hooks: Sequence[Hook]
    variable_status_hooks: List[VariableStatusHook]

    # Link to the containing modules object to be able to access the aggregated
    # variable statuses.
    modules: "Modules"

    @classmethod
    def from_path(
        cls, path: Path, deployment_target: str, modules: "Modules"
    ) -> "Module":
        module_root = path.parent.resolve()

        try:
            loader = ConfigLoader.get_loader_for_config_file(config_file_path=path)
            parser = ConfigParser(loader=loader)

            # Parse metadata
            name = parser.parse_name()
            version = parser.parse_version()
            enabled = parser.parse_enabled(deployment_target=deployment_target)
            documentation = parser.parse_documentation(
                deployment_target=deployment_target
            )

            # Parse variables
            variables = parser.parse_variables(deployment_target=deployment_target)

            # Parse links
            link_items = parser.parse_links(deployment_target=deployment_target)
            links = cls._create_links(link_items=link_items)

            # Parse shell script hooks
            shell_script_hook_items = parser.parse_shell_script_hooks(
                deployment_target=deployment_target
            )
            hooks = cls._create_shell_script_hooks(
                shell_script_hook_items=shell_script_hook_items
            )
            cls._validate_hooks(hooks=hooks)

            if links:
                hooks += cls._create_default_link_hooks(links=links)

            # Parse variable status hooks
            variable_status_hook_items = parser.parse_variable_status_hooks(
                deployment_target=deployment_target
            )
            variable_status_hooks = cls._create_variable_status_hooks(
                variable_status_hook_items=variable_status_hook_items
            )
        except LoaderError as e:
            raise ModuleError(f"Configuration loading error: {e}") from e
        except ParserError as e:
            raise ModuleError(f"Configuration syntax error: {e}") from e
        except Exception as e:
            raise ModuleError(
                f"Unexpected error happened during module loading: {e}"
            ) from e

        # Default the name to the directory name the module is in.
        if not name:
            name = module_root.name

        # Set default value for the missing version.
        if not version:
            version = "-"

        module = cls(
            name=name,
            version=version,
            enabled=enabled,
            documentation=documentation,
            variables=variables,
            root=module_root,
            links=links,
            hooks=hooks,
            variable_status_hooks=variable_status_hooks,
            modules=modules,
        )
        return module

    @staticmethod
    def _create_links(link_items: List[LinkItemDict]) -> List[LinkItem]:
        links = []
        for link_item in link_items:
            link = LinkItem(
                path_to_target=link_item["path_to_target"],
                path_to_symlink=link_item["path_to_symlink"],
                name=link_item["name"],
            )
            links.append(link)
        return links

    @staticmethod
    def _create_shell_script_hooks(
        shell_script_hook_items: List[ShellScriptHookItemDict],
    ) -> List[Union[ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]]:
        hooks: List[Union[ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]] = []
        for hook_item in shell_script_hook_items:
            hook = ShellScriptHook(
                path_to_script=hook_item["path_to_script"],
                priority=hook_item["priority"],
                name=hook_item["name"],
            )
            hooks.append(hook)
        return hooks

    @staticmethod
    def _create_variable_status_hooks(
        variable_status_hook_items: List[VariableStatusHookItemDict],
    ) -> List[VariableStatusHook]:
        hooks: List[VariableStatusHook] = []
        for hook_item in variable_status_hook_items:
            hook = VariableStatusHook(
                path_to_script=hook_item["path_to_script"],
                variable_name=hook_item["variable_name"],
                prepare_step_necessary=hook_item["prepare_step_necessary"],
            )
            hooks.append(hook)
        return hooks

    @staticmethod
    def _validate_hooks(
        hooks: List[Union[ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]],
    ) -> None:
        for index, _hook in enumerate(hooks, start=1):
            hook_name = _hook.hook_name
            if hook_name in [LinkDeploymentHook.NAME, LinkCleanUpHook.NAME]:
                raise ParserError(
                    f"Cannot use reserved hook name '{hook_name}' in section "
                    f"'hooks' at index {index}!"
                )

    @staticmethod
    def _create_default_link_hooks(
        links: List[LinkItem],
    ) -> List[Union[ShellScriptHook, LinkDeploymentHook, LinkCleanUpHook]]:
        return [
            LinkDeploymentHook(links=links),
            LinkCleanUpHook(links=links),
        ]

    @property
    def is_disabled(self) -> bool:
        return self.status == ModuleStatus.DISABLED

    @property
    def is_loading(self) -> bool:
        return self.status == ModuleStatus.LOADING

    @property
    def is_incomplete(self) -> bool:
        return self.status == ModuleStatus.INCOMPLETE

    @property
    def status(self) -> ModuleStatus:
        if not self.enabled:
            return ModuleStatus.DISABLED

        if self.errors:
            return ModuleStatus.ERROR

        links_state = []
        path_manager = PathManager(root_path=self.root)
        for link in self.links:
            links_state.append(
                link.check_if_link_exists(path_manager=path_manager)
                and link.check_if_target_matched(path_manager=path_manager)
            )

        variable_states = []
        for variable_name, variable_values in self.variables.items():
            for variable_value in variable_values:
                variable_status = self.modules.variable_statuses.get(
                    variable_name=variable_name, variable_value=variable_value
                )

                # If there is at least a variable loading, the whole module
                # status will be "loading".
                if variable_status.variable_is_loading:
                    return ModuleStatus.LOADING

                variable_states.append(variable_status.variable_was_added)

        if all(links_state + variable_states):
            return ModuleStatus.DEPLOYED

        return ModuleStatus.INCOMPLETE

    @property
    def errors(self) -> List[str]:
        path_manager = PathManager(root_path=self.root)
        errors = []
        for link in self.links:
            errors += link.report_errors(path_manager=path_manager)
        for hook in self.hooks:
            errors += hook.report_errors(path_manager=path_manager)
        return errors

    @property
    def warnings(self) -> List[str]:
        # TODO: implement this feature
        return []


class Modules:
    """
    Aggregation class that contains the loaded modules. It provides an interface
    to load the modules, and to collect the aggregated variables and hooks from
    them.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._flush_cache()

        if not settings.relative_modules_path:
            # TODO: raise better errors
            raise ModuleError("missing relative modules path definition")

        # Loading the modules from the config file paths.
        config_file_path_list = self._collect_config_file_paths(
            modules_root_path=settings.relative_modules_path,
            config_file_name=settings.config_file_name,
        )
        self._module_objects = self._load_module_objects(
            config_file_path_list=config_file_path_list,
            deployment_target=settings.deployment_target,
        )

        # Aggregating the variables.
        self._aggregated_variables = self._aggregate_variables(
            module_objects=self._module_objects
        )
        self._populate_variables_cache(aggregated_variables=self._aggregated_variables)

        # Aggregating the hooks.
        self._aggregated_hooks = self._aggregate_hooks(
            module_objects=self._module_objects, settings=settings
        )

        # Initializing the variable statuses subsystem.
        aggregated_variable_status_hooks = self._aggregate_variable_status_hooks(
            module_objects=self._module_objects, settings=settings
        )
        self.variable_statuses = VariableStatusManager(
            aggregated_variables=self._aggregated_variables,
            aggregated_variable_status_hooks=aggregated_variable_status_hooks,
            settings=self._settings,
        )
        self.variable_statuses.refresh_all()

    def __len__(self) -> int:
        return len(self._module_objects)

    def __getitem__(self, key: int) -> Module:
        return self._module_objects[key]

    def __iter__(self) -> Iterator[Module]:
        return iter(self._module_objects)

    def _load_module_objects(
        self, config_file_path_list: List[Path], deployment_target: str
    ) -> List[Module]:
        """
        Loader method that loads all modules from the list of configuration file
        paths respecting the passed deployment target.
        """
        module_objects: List[Module] = []

        for config_file_path in config_file_path_list:
            try:
                module = Module.from_path(
                    path=config_file_path,
                    deployment_target=deployment_target,
                    modules=self,
                )
            except ModuleError as e:
                raise ModuleError(
                    f"Error while loading module at path '{config_file_path}': {e}"
                ) from e
            module_objects.append(module)

        module_objects.sort(key=lambda m: str(m.root))

        return module_objects

    def _flush_cache(self) -> None:
        cache_directory = self._settings.dm_cache_root
        shutil.rmtree(cache_directory, ignore_errors=True)
        self._settings.dm_cache_root.mkdir(parents=True)

    def _populate_variables_cache(
        self, aggregated_variables: AggregatedVariablesType
    ) -> None:
        variables_cache_directory = self._settings.dm_cache_variables
        variables_cache_directory.mkdir(parents=True)
        for name, values in aggregated_variables.items():
            if re.search(r"\s", name):
                raise ValueError(
                    f"varibale name should not contain whitespace: '{name}'"
                )
            with open(variables_cache_directory / name, "w+") as f:
                for value in values:
                    f.write(f"{value}\n")

    @staticmethod
    def _aggregate_variables(module_objects: List[Module]) -> AggregatedVariablesType:
        """
        Function to aggregate variables from the loaded modules while
        deduplicating them.

        Disabled modules won't be agrregated.
        """
        vars: AggregatedVariablesType = defaultdict(list)
        for module in module_objects:
            if not module.enabled:
                continue
            for name, values in module.variables.items():
                for value in values:
                    if value not in vars[name]:
                        vars[name].append(value)

        for values in vars.values():
            values.sort()

        return dict(vars)

    @staticmethod
    def _aggregate_hooks(
        module_objects: List[Module],
        settings: Settings,
    ) -> AggregatedHooksType:
        """
        Function to collect the hooks from the loaded modules while groupping
        them together with their module objects. Hooks gets aggregated into
        lists by name ordered by priority.

        Disabled modules won't be agrregated.
        """
        hooks: AggregatedHooksType = OrderedDict()
        for module in module_objects:
            if not module.enabled:
                continue
            for hook in module.hooks:
                hook.initialize_execution_context(module=module, settings=settings)
                hook_name = hook.hook_name
                if hook_name not in hooks:
                    hooks[hook_name] = []
                hooks[hook_name].append(hook)
        for values in hooks.values():
            values.sort(key=lambda hook: hook.hook_priority)

        return hooks

    @staticmethod
    def _aggregate_variable_status_hooks(
        module_objects: List[Module],
        settings: Settings,
    ) -> AggregatedVariableStatusHooksType:
        """
        Function to collect the variable status hooks from the loaded modules.
        Duplicated variable status hooks for a variable is considered a
        configuration error.

        Disabled modules won't be aggregated.
        """
        variable_status_hooks = {}
        for module in module_objects:
            if not module.enabled:
                continue
            for hook in module.variable_status_hooks:
                if hook.variable_name in variable_status_hooks:
                    raise ModuleError(
                        "Multiple varible status hooks were defined for variable "
                        f"name '{hook.variable_name}'!"
                    )
                hook.initialize_execution_context(module=module, settings=settings)
                variable_status_hooks[hook.variable_name] = hook
        return variable_status_hooks

    @staticmethod
    def _collect_config_file_paths(
        modules_root_path: Path, config_file_name: str
    ) -> List[Path]:
        config_file_paths = list(modules_root_path.rglob(config_file_name))
        if config_file_paths:
            if modules_root_path / config_file_name in config_file_paths:
                raise ModuleError(
                    "You cannot have a config file directly in the main modules directory!"
                )
        return config_file_paths

    @property
    def aggregated_variables(self) -> AggregatedVariablesType:
        return self._aggregated_variables

    @property
    def aggregated_hooks(self) -> AggregatedHooksType:
        return self._aggregated_hooks
