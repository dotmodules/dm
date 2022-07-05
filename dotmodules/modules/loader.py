from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Type

# TODO: After python 3.11 tomllib will be in the standard library and this
# import should be changed to 'import tomllib'.
# https://docs.python.org/3.11/library/tomllib.html
import toml as tomllib


class LoaderError(Exception):
    pass


class ConfigLoader(ABC):
    @abstractmethod
    def __init__(self, config_file_path: Path) -> None:
        """
        The config loader will be called with only the path to the
        configurations file.
        """

    @staticmethod
    @abstractmethod
    def can_load(config_file_path: Path) -> bool:
        """
        Should return a True value if the given loader can process the given
        file. Based on this decision, the loader selection mechanism will
        instantiate the appropriate loader.
        """

    @abstractmethod
    def get(self, key: str) -> Any:
        """
        The only interface method the loader class hsould provide in orter to be
        able to get a value for a key from the loaded configuration file.

        The returned value should be constructed from the built in data
        structures: scalar values, lists or dictionaries.
        """

    @classmethod
    def get_loader_for_config_file(cls, config_file_path: Path) -> "ConfigLoader":
        selected_loaders: List[Type["ConfigLoader"]] = []

        if not config_file_path.is_file():
            raise LoaderError(
                f"Config file at path '{config_file_path}' does not exist!"
            )

        for loader_class in cls.__subclasses__():
            if loader_class.can_load(config_file_path=config_file_path):
                selected_loaders.append(loader_class)

        if len(selected_loaders) == 1:
            loader_class = selected_loaders[0]
            return loader_class(config_file_path=config_file_path)
        else:
            loaders = ", ".join([loader.__name__ for loader in selected_loaders])
            raise LoaderError(
                f"Multiple loaders ({loaders}) were selected for path '{config_file_path}'!"
            )


class TomlLoader(ConfigLoader):
    def __init__(self, config_file_path: Path) -> None:
        try:
            with open(config_file_path) as f:
                self.data: Dict[str, Any] = tomllib.load(f)
        except Exception as e:
            raise LoaderError(f"Toml loading error: {e}") from e

    @staticmethod
    def can_load(config_file_path: Path) -> bool:
        return str(config_file_path).endswith("toml")

    def get(self, key: str) -> Any:
        try:
            return self.data[key]
        except KeyError as e:
            raise LoaderError(f"Cannot retrieve key '{key}'!") from e
