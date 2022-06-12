from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict, TypeVar, Union

from dotmodules.modules.loader import ConfigLoader, LoaderError


class LinkItemDict(TypedDict):
    path_to_file: str
    path_to_symlink: str
    name: str


class HookItemDict(TypedDict):
    path_to_script: str
    priority: int
    name: str


T = TypeVar("T", bound=Union[LinkItemDict, HookItemDict])


class ParserError(Exception):
    """
    Error raised by the parser indicating an invalid config file syntax.
    """


@dataclass
class ConfigParser:
    """
    Parser class that parses and validates the configuration data received
    through the passed loader object.
    """

    loader: ConfigLoader

    class Definition:
        KEY__NAME = "name"
        KEY__VERSION = "version"
        KEY__ENABLED = "enabled"
        KEY__DOCUMENTATION = "documentation"
        KEY__VARIABLES = "variables"
        KEY__LINKS = "links"
        KEY__HOOKS = "hooks"

        EXPECTED_LINK_ITEM: LinkItemDict = {
            "path_to_file": "string",
            "path_to_symlink": "string",
            "name": "string",
        }

        EXPECTED_HOOK_ITEM: HookItemDict = {
            "path_to_script": "string",
            "name": "string",
            "priority": 0,
        }

    def parse_name(self) -> str:
        return self._parse_string(key=self.Definition.KEY__NAME)

    def parse_version(self) -> str:
        return self._parse_string(key=self.Definition.KEY__VERSION)

    def parse_enabled(self) -> bool:
        return self._parse_boolean(key=self.Definition.KEY__ENABLED)

    def parse_documentation(self) -> List[str]:
        return self._parse_string(
            key=self.Definition.KEY__DOCUMENTATION, mandatory=False
        ).splitlines()

    def parse_variables(self) -> Dict[str, List[str]]:
        try:
            variables = self.loader.get(key=self.Definition.KEY__VARIABLES)
        except LoaderError:
            # Variables are optional, a missing key would return an empty
            # dictionary.
            return {}

        variables_is_a_dict = isinstance(variables, dict)
        if not variables_is_a_dict:
            raise ParserError(
                "The '{}' section should have the following syntax: 'VARIABLE_NAME' = ['var_1', 'var_2', ..] !".format(
                    self.Definition.KEY__VARIABLES
                )
            )

        variable_names_are_strings = all(
            [isinstance(key, str) for key in variables.keys()]
        )
        if not variable_names_are_strings:
            raise ParserError(
                "The '{}' section should only have string variable names!".format(
                    self.Definition.KEY__VARIABLES
                )
            )

        validated_variables = {}
        error_message = "The '{}' section should contain a single string or a list of strings for a variable name!".format(
            self.Definition.KEY__VARIABLES
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
                    raise ParserError(error_message)
            else:
                raise ParserError(error_message)
        return validated_variables

    def parse_links(self) -> List[LinkItemDict]:
        return self._parse_item_list(
            key=self.Definition.KEY__LINKS,
            expected_item=self.Definition.EXPECTED_LINK_ITEM,
        )

    def parse_hooks(self) -> List[HookItemDict]:
        return self._parse_item_list(
            key=self.Definition.KEY__HOOKS,
            expected_item=self.Definition.EXPECTED_HOOK_ITEM,
        )

    def _parse_string(self, key: str, mandatory: bool = True) -> str:
        try:
            value = self.loader.get(key=key)
        except LoaderError as e:
            if not mandatory:
                return ""
            raise ParserError(f"Mandatory '{key}' section is missing!") from e

        if not value:
            if not mandatory:
                return ""
            raise ParserError(f"Empty value for section '{key}'!")

        if not isinstance(value, str):
            raise ParserError(
                f"Value for section '{key}' should be a string, got '{value}'!"
            )

        return value

    def _parse_boolean(self, key: str, mandatory: bool = True) -> bool:
        try:
            value = self.loader.get(key=key)
        except LoaderError as e:
            if not mandatory:
                return False
            raise ParserError(f"Mandatory '{key}' section is missing!") from e

        if not isinstance(value, bool):
            raise ParserError(
                f"Value for section '{key}' should be a boolean, got '{value}'!"
            )

        return value

    def _parse_item_list(
        self,
        key: str,
        expected_item: T,
    ) -> List[T]:
        try:
            raw_items = self.loader.get(key=key)
        except LoaderError:
            return []

        if not raw_items:
            return []

        self._assert_raw_items_type(key=key, raw_items=raw_items)

        items = []
        for index, raw_item in enumerate(raw_items, start=1):
            self._assert_for_mandatory_keys(
                key=key, expected_item=expected_item, index=index, raw_item=raw_item
            )
            self._assert_no_additional_keys(
                key=key, expected_item=expected_item, index=index, raw_item=raw_item
            )
            self._assert_value_types(
                key=key, expected_item=expected_item, index=index, raw_item=raw_item
            )
            items.append(raw_item)
        return items

    def _assert_value_types(
        self, key: str, expected_item: T, index: int, raw_item: Any
    ) -> None:
        for value_key, value in expected_item.items():
            if not isinstance(raw_item[value_key], type(value)):
                raise ParserError(
                    f"The value for field '{value_key}' should be an {type(value).__name__} in section '{key}' item at index {index}!"
                )

    def _assert_no_additional_keys(
        self, key: str, expected_item: T, index: int, raw_item: Any
    ) -> None:
        additional_keys = list(
            set(raw_item.keys()).difference(set(expected_item.keys()))
        )
        if len(additional_keys) == 1:
            raise ParserError(
                f"Unexpected field '{additional_keys[0]}' found for section '{key}' item at index {index}!"
            )
        if len(additional_keys) > 1:
            formatted_keys = ", ".join([f"'{key}'" for key in sorted(additional_keys)])
            raise ParserError(
                f"Unexpected fields {formatted_keys} found for section '{key}' item at index {index}!"
            )

    def _assert_for_mandatory_keys(
        self, key: str, expected_item: T, index: int, raw_item: Any
    ) -> None:
        """
        Assert if every mandatory key exists.
        """
        for mandatory_key in expected_item.keys():
            if mandatory_key not in raw_item:
                raise ParserError(
                    f"Missing mandatory field '{mandatory_key}' from section '{key}' item at index {index}!"
                )

    def _assert_raw_items_type(self, key: str, raw_items: Any) -> None:
        if not isinstance(raw_items, list):
            raise ParserError(
                f"Invalid value for '{key}'! It should contain a list of objects!"
            )
        else:
            if not all([isinstance(item, dict) for item in raw_items]):
                raise ParserError(
                    f"Invalid value for '{key}'! It should contain a list of objects!"
                )
