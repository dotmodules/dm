import os
from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Generator, List, Optional, Type, cast

# TODO: After python 3.11 'tomllib' will be available from the standard library.
# This library import hack can be removed then.
import tomllib
from dotmodules.settings import Settings
from dotmodules.shell_adapter import ShellAdapter


@dataclass
class LinkItem:
    # From module config.
    path_to_file: str
    path_to_symlink: str
    name: str = "link"

    # Additional fields.
    module_root: Path = field(init=False)

    @property
    def full_path_to_file(self) -> Path:
        """
        The path to file should be relative to the module root directory.
        """
        full_path = self.module_root / self.path_to_file
        if not full_path.is_file():
            raise ValueError(
                f"Link.path_to_file does not name a file: '{self.path_to_file}'"
            )
        return full_path

    @property
    def full_path_to_symlink(self) -> Path:
        """
        The path to symlink should be an absolute path with the the option to
        resolve the '$HOME' variable to the users home directory.
        """
        home_directory = str(Path.home())
        resolved_path_to_symlink_str = self.path_to_symlink.replace(
            "$HOME", home_directory
        )
        resolved_path_to_symlink = Path(resolved_path_to_symlink_str)
        if not resolved_path_to_symlink.is_absolute():
            raise ValueError(
                f"Link.path_to_symlink should be an absolute path: '{resolved_path_to_symlink_str}'"
            )
        return resolved_path_to_symlink

    @property
    def present(self) -> bool:
        return self.full_path_to_symlink.is_symlink()

    @property
    def target_matched(self) -> bool:
        return (
            self.present
            and self.full_path_to_symlink.resolve() == self.full_path_to_file
        )


class Hook(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_priority(self) -> int:
        pass

    @abstractmethod
    def get_details(self) -> str:
        pass

    @abstractmethod
    def get_module_name(self) -> str:
        pass

    @abstractmethod
    def execute(self, settings: Settings) -> int:
        pass


@dataclass
class ShellScriptHook(Hook):
    # From module config.
    path_to_script: str
    name: str = "hook"
    priority: int = 0

    # Additional fields.
    module_name: str = field(init=False)
    module_root: Path = field(init=False)

    def get_name(self) -> str:
        return self.name

    def get_priority(self) -> int:
        return self.priority

    def get_details(self) -> str:
        return self.path_to_script

    def get_module_name(self) -> str:
        return self.module_name

    @property
    def full_path_to_script(self) -> Path:
        """
        The path to script should be relative to the module root directory.
        """
        full_path = self.module_root / self.path_to_script
        if not full_path.is_file():
            raise ValueError(
                f"Hook.path_to_script does not name a file: '{self.path_to_script}'"
            )
        return full_path

    def execute(self, settings: Settings) -> int:
        adapter = ShellAdapter()
        # Getting the absolute path for the hook adapter script.
        absolute_hook_adapter_script = Path(
            "./utils/dm_hook__shell_script_adapter.sh"
        ).resolve()
        # Calculating the relative path from the module's root the dm repository
        # root which is the current working directory as the hook will be
        # executed from the given module's root directory.
        relative_dm_repo_root = os.path.relpath(os.getcwd(), self.module_root)

        command = [
            str(absolute_hook_adapter_script),  # 0 - hook adapter script path
            str(relative_dm_repo_root),  # 1 - DM_REPO_ROOT
            str(self.name),  # 2 - dm__config__target_hook_name
            str(self.priority),  # 3 - dm__config__target_hook_priority
            str(self.module_name),  # 4 - dm__config__target_module_name
            str(settings.dm_cache_root),  # 5 - dm__config__dm_cache_root
            str(settings.dm_cache_variables),  # 6 - dm__config__dm_cache_variables
            str(settings.indent),  # 7 - dm__config__indent
            str(settings.text_wrap_limit),  # 8 - dm__config__wrap_limit
            str(self.full_path_to_script),  # 9 - dm__config__target_hook_script
        ]
        status_code = adapter.execute_interactively(
            command=command, cwd=self.module_root
        )
        return status_code


@dataclass
class LinkDeploymentHook(Hook):
    NAME = "DEPLOY_LINKS"
    PRIORITY = 0

    links: List[LinkItem]
    module_name: str
    module_root: Path

    def get_name(self) -> str:
        return self.NAME

    def get_priority(self) -> int:
        return self.PRIORITY

    def get_details(self) -> str:
        link_count = len(self.links)
        if link_count == 1:
            return f"Deploy {len(self.links)} link"
        else:
            return f"Deploy {len(self.links)} links"

    def get_module_name(self) -> str:
        return self.module_name

    def execute(self, settings: Settings) -> int:
        adapter = ShellAdapter()
        # Getting the absolute path for the hook adapter script.
        absolute_hook_adapter_script = Path(
            "./utils/dm_hook__link_deployment_adapter.sh"
        ).resolve()
        # Calculating the relative path from the module's root the dm repository
        # root which is the current working directory as the hook will be
        # executed from the given module's root directory.
        relative_dm_repo_root = os.path.relpath(os.getcwd(), self.module_root)

        command = [
            str(absolute_hook_adapter_script),  # 0 - hook adapter script path
            str(relative_dm_repo_root),  # 1 - DM_REPO_ROOT
            str(self.get_name()),  # 2 - dm__config__target_hook_name
            str(self.get_priority()),  # 3 - dm__config__target_hook_priority
            str(self.get_module_name()),  # 4 - dm__config__target_module_name
            str(settings.dm_cache_root),  # 5 - dm__config__dm_cache_root
            str(settings.dm_cache_variables),  # 6 - dm__config__dm_cache_variables
            str(settings.indent),  # 7 - dm__config__indent
            str(settings.text_wrap_limit),  # 8 - dm__config__wrap_limit
        ]
        for link in self.links:
            command.append(str(link.full_path_to_file))
            command.append(str(link.full_path_to_symlink))
        status_code = adapter.execute_interactively(
            command=command, cwd=self.module_root
        )
        return status_code


class ConfigError(Exception):
    pass


RawSimpleConfigDataType = str
RawVariablesConfigDataType = Dict[str, str | List[str]]
RawObjectListConfigDataType = List[Dict[str, str | int]]
RawCommonConfigDataType = Dict[
    str,
    Optional[
        RawSimpleConfigDataType
        | RawVariablesConfigDataType
        | RawObjectListConfigDataType
    ],
]
ParsedVariablesConfigDataType = Dict[str, List[str]]


class ConfigLoader:
    @staticmethod
    def load_raw_config_data(
        config_file_path: Path,
    ) -> RawCommonConfigDataType:
        try:
            with open(config_file_path) as f:
                return tomllib.load(f)
        except Exception as e:
            raise ConfigError(f"configuration loading error: {e}") from e


class ConfigParser:
    """
    Inner class that can be used to parse, condition and validate the raw
    configuration files.
    """

    KEY__NAME = "name"
    KEY__VERSION = "version"
    KEY__DOCUMENTATION = "documentation"
    KEY__VARIABLES = "variables"
    KEY__LINKS = "links"
    KEY__HOOKS = "hooks"

    @classmethod
    def parse_name(cls, data: RawCommonConfigDataType) -> str:
        return cls._parse_string(data=data, key=cls.KEY__NAME)

    @classmethod
    def parse_version(cls, data: RawCommonConfigDataType) -> str:
        return cls._parse_string(data=data, key=cls.KEY__VERSION)

    @classmethod
    def parse_documentation(cls, data: RawCommonConfigDataType) -> List[str]:
        return cls._parse_string(
            data=data, key=cls.KEY__DOCUMENTATION, mandatory=False
        ).splitlines()

    @classmethod
    def parse_variables(
        cls, data: RawCommonConfigDataType
    ) -> ParsedVariablesConfigDataType:
        variables = data.get(cls.KEY__VARIABLES) or {}
        variables = cast(RawVariablesConfigDataType, variables)

        variables_is_a_dict = isinstance(variables, dict)
        if not variables_is_a_dict:
            raise SyntaxError(
                "the '{}' section should have the following syntax: 'VARIABLE_NAME' = ['var_1', 'var_2', ..]".format(
                    cls.KEY__VARIABLES
                )
            )

        variable_names_are_strings = all(
            [isinstance(key, str) for key in variables.keys()]
        )
        if not variable_names_are_strings:
            raise SyntaxError(
                "the '{}' section should only have string variable names".format(
                    cls.KEY__VARIABLES
                )
            )

        validated_variables = {}
        error_message = "the '{}' section should contain a single string or a list of strings for a variable name".format(
            cls.KEY__VARIABLES
        )
        for key, value in variables.items():
            if isinstance(value, str):
                validated_variables[key] = [value]
            elif isinstance(value, list):
                if all(
                    [
                        isinstance(item, str)
                        for item_list in variables.values()
                        for item in item_list
                    ]
                ):
                    validated_variables[key] = value
                else:
                    raise ValueError(error_message)
            else:
                raise ValueError(error_message)
        return validated_variables

    @classmethod
    def parse_links(
        cls, data: RawCommonConfigDataType, module_root: Path
    ) -> List[LinkItem]:
        links = cast(
            List[LinkItem],
            cls._parse_item_list(data=data, key=cls.KEY__LINKS, item_class=LinkItem),
        )
        for link in links:
            link.module_root = module_root
        return links

    @classmethod
    def parse_hooks(
        cls, data: RawCommonConfigDataType, module_root: Path, module_name: str
    ) -> List[ShellScriptHook]:
        hooks = cast(
            List[ShellScriptHook],
            cls._parse_item_list(
                data=data, key=cls.KEY__HOOKS, item_class=ShellScriptHook
            ),
        )
        for hook in hooks:
            hook.module_name = module_name
            hook.module_root = module_root
        return hooks

    @classmethod
    def _parse_string(
        cls, data: RawCommonConfigDataType, key: str, mandatory: bool = True
    ) -> str:
        if key not in data:
            if not mandatory:
                return ""
            raise SyntaxError(f"mandatory '{key}' section is missing")
        value = data[key]
        if not value:
            if not mandatory:
                return ""
            raise ValueError(f"empty value for section '{key}'")
        if not isinstance(value, str):
            raise ValueError(f"value for section '{key}' should be a string")
        return value

    @classmethod
    def _parse_item_list(
        cls,
        data: RawCommonConfigDataType,
        key: str,
        item_class: Type[LinkItem] | Type[ShellScriptHook],
    ) -> List[LinkItem | ShellScriptHook]:
        raw_items = data.get(key) or []
        raw_items = cast(RawObjectListConfigDataType, raw_items)
        items = []
        for index, raw_item in enumerate(raw_items, start=1):
            try:
                # This solution is hard for mypy to understand. Ignoring the
                # type checking here..
                item = item_class(**raw_item)  # type: ignore
            except Exception as e:
                message = "unexpected error happened while processing '{key}' item at index '{index}': '{reason}'".format(
                    key=key, index=index, reason=str(e)
                )
                raise SyntaxError(message) from e
            items.append(item)
        return items


@dataclass
class Module:
    name: str
    version: str
    documentation: List[str]
    variables: Dict[str, List[str]]
    links: List[LinkItem]
    hooks: List[Hook]
    root: Path

    @classmethod
    def from_path(cls, path: Path) -> "Module":
        module_root = path.parent.resolve()

        data = ConfigLoader.load_raw_config_data(config_file_path=path)

        try:
            name = ConfigParser.parse_name(data=data)
            version = ConfigParser.parse_version(data=data)
            documentation = ConfigParser.parse_documentation(data=data)
            variables = ConfigParser.parse_variables(data=data)
            links = ConfigParser.parse_links(data=data, module_root=module_root)
            hooks = ConfigParser.parse_hooks(
                data=data, module_name=name, module_root=module_root
            )
        except SyntaxError as e:
            raise ConfigError(f"configuration syntax error: {e}") from e
        except ValueError as e:
            raise ConfigError(f"configuration value error: {e}") from e
        except Exception as e:
            raise ConfigError(
                f"unexpected error happened during configuration parsing: {e}"
            ) from e

        ret = cls(
            name=name,
            version=version,
            documentation=documentation,
            variables=variables,
            links=links,
            hooks=cast(List[Hook], hooks),
            root=module_root,
        )
        return ret

    def validate(self) -> None:
        """
        The link deployment hook is an auto generated hook. Its name is
        reserved.
        """
        for hook in self.hooks:
            hook_name = hook.get_name()
            if hook_name == LinkDeploymentHook.NAME:
                raise ValueError(
                    f"Cannot use reserved hook name '{LinkDeploymentHook.NAME}'!"
                )

    def add_link_deployment_hook(self) -> None:
        """
        Appending the link deplyment hook to the hooks if there are links to
        deploy.
        """
        if self.links:
            link_deployment_hook = LinkDeploymentHook(
                links=self.links,
                module_name=self.name,
                module_root=self.root,
            )
            self.hooks.append(link_deployment_hook)


class Modules:
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
            module.validate()
            module.add_link_deployment_hook()
            modules.modules.append(module)

        # Sorting the modules in alphabetical path order.
        modules.modules.sort(key=lambda m: str(m.root))
        return modules

    @property
    def variables(self) -> Dict[str, List[str]]:
        vars = {}
        for module in self.modules:
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
            for hook in module.hooks:
                hook_name = hook.get_name()
                if hook_name not in hooks:
                    hooks[hook_name] = []
                hooks[hook_name].append(hook)
        for _, values in hooks.items():
            values.sort(key=lambda item: item.get_priority())

        return hooks
