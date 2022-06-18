from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Generator, List, Sequence

from dotmodules.modules.hooks import (
    Hook,
    LinkCleanUpHook,
    LinkDeploymentHook,
    ShellScriptHook,
)
from dotmodules.modules.links import LinkItem
from dotmodules.modules.loader import ConfigLoader, LoaderError
from dotmodules.modules.parser import (
    ConfigParser,
    HookItemDict,
    LinkItemDict,
    ParserError,
)
from dotmodules.modules.path import PathManager


class ModuleError(Exception):
    """
    Exception that will be raised on module level errors.
    """


class ModuleStatus(str, Enum):
    DISABLED: str = "disabled"
    DEPLOYED: str = "deployed"
    PENDING: str = "pending"
    ERROR: str = "error"


@dataclass
class Module:
    root: Path
    name: str
    version: str
    enabled: bool
    documentation: Sequence[str]
    variables: Dict[str, List[str]]
    links: Sequence[LinkItem]
    hooks: Sequence[Hook]

    @classmethod
    def from_path(cls, path: Path) -> "Module":
        module_root = path.parent.resolve()

        try:
            loader = ConfigLoader.get_loader_for_config_file(config_file_path=path)
            parser = ConfigParser(loader=loader)

            name = parser.parse_name()
            version = parser.parse_version()
            enabled = parser.parse_enabled()
            documentation = parser.parse_documentation()
            variables = parser.parse_variables()
            link_items = parser.parse_links()
            hook_items = parser.parse_hooks()

            links = cls._create_links(link_items=link_items)
            hooks = cls._create_hooks(hook_items=hook_items)
            cls._validate_hooks(hooks=hooks)

            if links:
                hooks += cls._create_default_link_hooks(links=links)

        except LoaderError as e:
            raise ModuleError(f"Configuration loading error: {e}") from e
        except ParserError as e:
            raise ModuleError(f"Configuration syntax error: {e}") from e
        except Exception as e:
            raise ModuleError(
                f"Unexpected error happened during module loading: {e}"
            ) from e

        module = cls(
            name=name,
            version=version,
            enabled=enabled,
            documentation=documentation,
            variables=variables,
            root=module_root,
            links=links,
            hooks=hooks,
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
    def _create_hooks(
        hook_items: List[HookItemDict],
    ) -> List[ShellScriptHook | LinkDeploymentHook | LinkCleanUpHook]:
        hooks: List[ShellScriptHook | LinkDeploymentHook | LinkCleanUpHook] = []
        for hook_item in hook_items:
            hook = ShellScriptHook(
                path_to_script=hook_item["path_to_script"],
                priority=hook_item["priority"],
                name=hook_item["name"],
            )
            hooks.append(hook)
        return hooks

    @staticmethod
    def _validate_hooks(
        hooks: List[ShellScriptHook | LinkDeploymentHook | LinkCleanUpHook],
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
    ) -> List[ShellScriptHook | LinkDeploymentHook | LinkCleanUpHook]:
        return [
            LinkDeploymentHook(links=links),
            LinkCleanUpHook(links=links),
        ]

    @property
    def status(self) -> ModuleStatus:
        if self.errors:
            return ModuleStatus.ERROR

        if not self.enabled:
            return ModuleStatus.DISABLED

        path_manager = PathManager(root_path=self.root)
        if all(
            [
                link.check_if_link_exists(path_manager=path_manager)
                and link.check_if_target_matched(path_manager=path_manager)
                for link in self.links
            ]
        ):
            return ModuleStatus.DEPLOYED

        return ModuleStatus.PENDING

    @property
    def errors(self) -> List[str]:
        path_manager = PathManager(root_path=self.root)
        errors = []
        for link in self.links:
            errors += link.report_errors(path_manager=path_manager)
        for hook in self.hooks:
            errors += hook.report_errors(path_manager=path_manager)
        return errors


@dataclass
class HookAggregate:
    module: Module
    hook: Hook


class Modules:
    """
    Aggregation class that contains the loaded modules. It provides an interface
    to load the modules, and to collect the aggregated variables and hooks from
    them.
    """

    def __init__(self) -> None:
        self.modules: List[Module] = []

    def __len__(self) -> int:
        return len(self.modules)

    @staticmethod
    def _config_file_paths(
        modules_root_path: Path, config_file_name: str
    ) -> Generator[Path, None, None]:
        return Path(modules_root_path).rglob(config_file_name)

    @classmethod
    def load(cls, modules_root_path: Path, config_file_name: str) -> "Modules":
        modules = cls()
        config_file_paths = cls._config_file_paths(
            modules_root_path=modules_root_path, config_file_name=config_file_name
        )
        for config_file_path in config_file_paths:
            try:
                module = Module.from_path(path=config_file_path)
            except ModuleError as e:
                raise ModuleError(
                    f"Error while loading module at path '{config_file_path}': {e}"
                ) from e
            modules.modules.append(module)

        # Sorting the modules in alphabetical path order.
        modules.modules.sort(key=lambda m: str(m.root))
        return modules

    @property
    def variables(self) -> Dict[str, List[str]]:
        vars = {}
        for module in self.modules:
            if not module.enabled:
                continue
            for name, values in module.variables.items():
                if name not in vars:
                    vars[name] = list(values)
                else:
                    for value in values:
                        if value not in vars[name]:
                            vars[name] += values
                    vars[name].sort()

        return vars

    @property
    def hooks(self) -> OrderedDict[str, List[HookAggregate]]:
        hooks: OrderedDict[str, List[HookAggregate]] = OrderedDict()
        for module in self.modules:
            if not module.enabled:
                continue
            for hook in module.hooks:
                hook_name = hook.hook_name
                if hook_name not in hooks:
                    hooks[hook_name] = []
                hooks[hook_name].append(HookAggregate(module=module, hook=hook))
        for _, values in hooks.items():
            values.sort(key=lambda item: item.hook.hook_priority)

        return hooks
