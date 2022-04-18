from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Generator, List, Type, cast

# TODO: After python 3.11 'tomllib' will be available from the standard library.
# This library import hack can be removed then.
import tomllib


@dataclass
class LinkItem:
    # From module config.
    path_to_file: str
    path_to_symlink: str
    name: str = "link"

    # Additional fields.
    module_root: Path = field(init=False)

    @property
    def full_path_to_file(self):
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
    def full_path_to_symlink(self):
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

    def validate_for_root(self, module_root: Path):
        pass


@dataclass
class HookItem:
    # From module config.
    name: str
    path_to_script: str
    priority: int = 0

    # Additional fields.
    module_root: Path = field(init=False)


class ConfigError(Exception):
    pass


class ConfigLoader:
    @staticmethod
    def load_raw_config_data(config_file_path: Path) -> dict:
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
    def parse_name(cls, data: dict) -> str:
        return cls._parse_string(data=data, key=cls.KEY__NAME)

    @classmethod
    def parse_version(cls, data: dict) -> str:
        return cls._parse_string(data=data, key=cls.KEY__VERSION)

    @classmethod
    def parse_documentation(cls, data: dict) -> List[str]:
        return cls._parse_string(
            data=data, key=cls.KEY__DOCUMENTATION, mandatory=False
        ).splitlines()

    @classmethod
    def parse_variables(cls, data: dict) -> Dict[str, List[str]]:
        variables = data.get(cls.KEY__VARIABLES) or {}

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
    def parse_links(cls, data: dict, module_root: Path) -> List[LinkItem]:
        links = cast(
            List[LinkItem],
            cls._parse_item_list(data=data, key=cls.KEY__LINKS, item_class=LinkItem),
        )
        for link in links:
            link.module_root = module_root
        return links

    @classmethod
    def parse_hooks(cls, data: dict, module_root: Path) -> List[HookItem]:
        return cast(
            List[HookItem],
            cls._parse_item_list(data=data, key=cls.KEY__HOOKS, item_class=HookItem),
        )

    @classmethod
    def _parse_string(cls, data: dict, key: str, mandatory: bool = True) -> str:
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
        cls, data: dict, key: str, item_class: Type[LinkItem] | Type[HookItem]
    ) -> List[LinkItem | HookItem]:
        raw_items = data.get(key) or []
        items = []
        for index, raw_item in enumerate(raw_items, start=1):
            try:
                item = item_class(**raw_item)
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
    hooks: List[HookItem]
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
            hooks = ConfigParser.parse_hooks(data=data, module_root=module_root)
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
            hooks=hooks,
            root=module_root,
        )
        return ret


class Modules:
    def __init__(self):
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
    def variables(self):
        vars = {}
        for module in self.modules:
            for name, values in module.variables.items():
                if name not in vars:
                    vars[name] = list(values)
                else:
                    vars[name] += values
                    vars[name].sort()

        return vars
