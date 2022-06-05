import os
from abc import ABC, abstractmethod, abstractproperty, abstractstaticmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Type, cast

from dotmodules.settings import Settings
from dotmodules.shell_adapter import ShellAdapter

from .hooks import Hook, LinkCleanUpHook, LinkDeploymentHook, ShellScriptHook
from .links import LinkItem
from .loader import ConfigLoader


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
    documentation: List[str]
    variables: Dict[str, List[str]]
    links: List[LinkItem]
    hooks: List[Hook]

    @classmethod
    def from_path(cls, path: Path) -> "Module":
        module_root = path.parent.resolve()

        loader = ConfigLoader.load_raw_config_data(config_file_path=path)

        try:
            name = ConfigParser.parse_name(data=data)
            version = ConfigParser.parse_version(data=data)
            enabled = ConfigParser.parse_enabled(data=data)
            documentation = ConfigParser.parse_documentation(data=data)
            variables = ConfigParser.parse_variables(data=data)
            links = ConfigParser.parse_links(data=data)
            hooks = ConfigParser.parse_hooks(data=data)
        except SyntaxError as e:
            raise ConfigError(f"configuration syntax error: {e}") from e
        except ValueError as e:
            raise ConfigError(f"configuration value error: {e}") from e
        except Exception as e:
            raise ConfigError(
                f"unexpected error happened during configuration parsing: {e}"
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
        module.add_default_hooks()
        return module

    def add_default_hooks(self) -> None:
        """
        Adding the default hooks to the modules.
        """
        for hook in self.hooks:
            hook_name = hook.hook_name
            if hook_name in [LinkDeploymentHook.NAME, LinkCleanUpHook.NAME]:
                raise ValueError(f"Cannot use reserved hook name '{hook_name}'!")

        if self.links:
            link_deployment_hook = LinkDeploymentHook(links=self.links)
            self.hooks.append(link_deployment_hook)

            link_clean_up_hook = LinkCleanUpHook(links=self.links)
            self.hooks.append(link_clean_up_hook)

    @property
    def status(self) -> ModuleStatus:
        if self.errors:
            return ModuleStatus.ERROR
        if not self.enabled:
            return ModuleStatus.DISABLED
        if all([link.deployed for link in self.links]):
            return ModuleStatus.DEPLOYED
        return ModuleStatus.PENDING

    @property
    def errors(self) -> List[str]:
        errors = []
        for link in self.links:
            errors += link.validate()
        for hook in self.hooks:
            errors += hook.validate()
        return errors


class Modules:
    """
    Aggregation class that contains all the parsed modules. It provides an
    interface to load the modules, and to collect the aggregated variables and
    hooks from them.
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
            module = Module.from_path(path=config_file_path)
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
                    vars[name] += values
                    vars[name].sort()

        return vars

    @property
    def hooks(self) -> OrderedDict[str, List[Hook]]:
        hooks: OrderedDict[str, List[Hook]] = OrderedDict()
        for module in self.modules:
            if not module.enabled:
                continue
            for hook in module.hooks:
                hook_name = hook.hook_name
                if hook_name not in hooks:
                    hooks[hook_name] = []
                hooks[hook_name].append(hook)
        for _, values in hooks.items():
            values.sort(key=lambda item: item.get_priority())

        return hooks
