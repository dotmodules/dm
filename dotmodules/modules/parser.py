from dataclasses import dataclass
from typing import Any, Dict, List, TypedDict, TypeVar, Union

from dotmodules.modules.loader import ConfigLoader, LoaderError


class LinkItemDict(TypedDict):
    path_to_target: str
    path_to_symlink: str
    name: str


class ShellScriptHookItemDict(TypedDict):
    path_to_script: str
    priority: int
    name: str


class VariableStatusHookItemDict(TypedDict):
    path_to_script: str
    variable_name: str
    prepare_step_necessary: bool


T = TypeVar(
    "T",
    bound=Union[LinkItemDict, ShellScriptHookItemDict, VariableStatusHookItemDict],
)


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
        KEY__SHELL_SCRIPT_HOOKS = "shell_script_hooks"
        KEY__VARIABLE_STATUS_HOOKS = "variable_status_hooks"

        TEMPLATE__DOCUMENTATION = "documentation__{deployment_target}"
        TEMPLATE__VARIABLES = "variables__{deployment_target}"
        TEMPLATE__LINKS = "links__{deployment_target}"
        TEMPLATE__SHELL_SCRIPT_HOOKS = "shell_script_hooks__{deployment_target}"
        TEMPLATE__VARIABLE_STATUS_HOOKS = "variable_status_hooks__{deployment_target}"

        # NOTE: In the following definitions the type of the values will
        # determine the expected value type.
        EXPECTED_LINK_ITEM: LinkItemDict = {
            "path_to_target": "string",
            "path_to_symlink": "string",
            "name": "string",
        }

        EXPECTED_SHELL_SCRIPT_HOOK_ITEM: ShellScriptHookItemDict = {
            "path_to_script": "string",
            "name": "string",
            "priority": 0,
        }

        EXPECTED_VARIABLE_STATUS_HOOK_ITEM: VariableStatusHookItemDict = {
            "path_to_script": "string",
            "variable_name": "string",
            "prepare_step_necessary": False,
        }

    def parse_name(self) -> str:
        return self._parse_string(key=self.Definition.KEY__NAME)

    def parse_version(self) -> str:
        return self._parse_string(key=self.Definition.KEY__VERSION)

    def parse_enabled(self, deployment_target: str) -> bool:
        """
        A module can be enabled globally or for different deployment targets
        specifically.

        Defining the enabled state is mandatory: either by specifying a global
        enabled state or break up the state definiton to different deployment
        targets.

        If you define the enabled state in deployment target specific way, you
        have to specify all used deployment targets. If you use a deployment
        target not specified in a module's enabled status definition, it is
        considered as a syntax error.
        """
        key = self.Definition.KEY__ENABLED
        try:
            value = self.loader.get(key=key)
        except LoaderError as e:
            raise ParserError(f"Mandatory section '{key}' is missing!") from e

        if isinstance(value, dict):
            if not deployment_target:
                raise ParserError(
                    f"Section '{key}' was defined for deployment targets only, but "
                    "there is no deployment target specified for the current deployment!"
                )

            if deployment_target not in value:
                raise ParserError(
                    f"Missing deployment target '{deployment_target}' from section '{key}'!"
                )

            value = value[deployment_target]

            if not isinstance(value, bool):
                raise ParserError(
                    f"The value for section '{key}' should be boolean for deployment "
                    f"target '{deployment_target}', got {type(value).__name__}!"
                )
        else:
            if not isinstance(value, bool):
                raise ParserError(
                    f"The value for section '{key}' should be boolean, got {type(value).__name__}!"
                )

        return value

    def parse_documentation(self, deployment_target: str) -> List[str]:
        docs = self._parse_string(
            key=self.Definition.KEY__DOCUMENTATION, mandatory=False
        ).splitlines()

        if deployment_target:
            key = self.Definition.TEMPLATE__DOCUMENTATION.format(
                deployment_target=deployment_target
            )
            targeted_docs = self._parse_string(key=key, mandatory=False).splitlines()
            if targeted_docs:
                # Adding an extra empty line if there are already documentation lines.
                if docs:
                    docs.append("")
                docs += targeted_docs

        return docs

    def parse_variables(self, deployment_target: str) -> Dict[str, List[str]]:
        raw_variables = self._load_global_variables()
        variables = self._validate_variables(variables=raw_variables)

        if deployment_target:
            raw_variables = self._load_deployment_target_variables(
                deployment_target=deployment_target
            )
            deployment_target_variables = self._validate_variables(
                variables=raw_variables
            )
            for key in deployment_target_variables.keys():
                if key in variables:
                    deployment_target_variables_section = (
                        self.Definition.TEMPLATE__VARIABLES.format(
                            deployment_target=deployment_target
                        )
                    )
                    raise ParserError(
                        "Deployment target specific variable section "
                        f"'{deployment_target_variables_section}' redefined already "
                        f"existing global variable key '{key}'!"
                    )
            variables.update(deployment_target_variables)

        return variables

    def _load_global_variables(self) -> Any:
        try:
            return self.loader.get(key=self.Definition.KEY__VARIABLES)
        except LoaderError:
            # Variables are optional, a missing key would result an empty
            # dictionary.
            return {}

    def _load_deployment_target_variables(self, deployment_target: str) -> Any:
        try:
            key = self.Definition.TEMPLATE__VARIABLES.format(
                deployment_target=deployment_target
            )
            return self.loader.get(key=key)
        except LoaderError:
            # Variables are optional, a missing key would result an empty
            # dictionary.
            return {}

    def _validate_variables(self, variables: Any) -> Dict[str, List[str]]:
        variables_is_a_dict = isinstance(variables, dict)
        if not variables_is_a_dict:
            raise ParserError(
                "The '{}' section should have the following syntax: 'VARIABLE_NAME' = ['var_1', 'var_2', ..] !".format(
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

    def parse_links(self, deployment_target: str) -> List[LinkItemDict]:
        links = self._parse_item_list(
            key=self.Definition.KEY__LINKS,
            expected_item=self.Definition.EXPECTED_LINK_ITEM,
        )

        if deployment_target:
            key = self.Definition.TEMPLATE__LINKS.format(
                deployment_target=deployment_target
            )
            deployment_target_links = self._parse_item_list(
                key=key,
                expected_item=self.Definition.EXPECTED_LINK_ITEM,
            )

            for deployment_target_link in deployment_target_links:
                if deployment_target_link in links:
                    deployment_target_link_section = (
                        self.Definition.TEMPLATE__LINKS.format(
                            deployment_target=deployment_target
                        )
                    )
                    raise ParserError(
                        "Deployment target specific link section "
                        f"'{deployment_target_link_section}' contains an already "
                        "defined link item!"
                    )

            links += deployment_target_links

        return links

    def parse_shell_script_hooks(
        self, deployment_target: str
    ) -> List[ShellScriptHookItemDict]:
        hooks = self._parse_item_list(
            key=self.Definition.KEY__SHELL_SCRIPT_HOOKS,
            expected_item=self.Definition.EXPECTED_SHELL_SCRIPT_HOOK_ITEM,
        )

        if deployment_target:
            key = self.Definition.TEMPLATE__SHELL_SCRIPT_HOOKS.format(
                deployment_target=deployment_target
            )
            deployment_target_hooks = self._parse_item_list(
                key=key,
                expected_item=self.Definition.EXPECTED_SHELL_SCRIPT_HOOK_ITEM,
            )

            for deployment_target_hook in deployment_target_hooks:
                if deployment_target_hook in hooks:
                    deployment_target_hook_section = (
                        self.Definition.TEMPLATE__SHELL_SCRIPT_HOOKS.format(
                            deployment_target=deployment_target
                        )
                    )
                    raise ParserError(
                        "Deployment target specific hook section "
                        f"'{deployment_target_hook_section}' contains an already "
                        "defined hook item!"
                    )

            hooks += deployment_target_hooks

        return hooks

    def parse_variable_status_hooks(
        self, deployment_target: str
    ) -> List[VariableStatusHookItemDict]:
        hooks = self._parse_item_list(
            key=self.Definition.KEY__VARIABLE_STATUS_HOOKS,
            expected_item=self.Definition.EXPECTED_VARIABLE_STATUS_HOOK_ITEM,
        )

        if deployment_target:
            key = self.Definition.TEMPLATE__VARIABLE_STATUS_HOOKS.format(
                deployment_target=deployment_target
            )
            deployment_target_hooks = self._parse_item_list(
                key=key,
                expected_item=self.Definition.EXPECTED_VARIABLE_STATUS_HOOK_ITEM,
            )

            for deployment_target_hook in deployment_target_hooks:
                if deployment_target_hook in hooks:
                    deployment_target_hook_section = (
                        self.Definition.TEMPLATE__VARIABLE_STATUS_HOOKS.format(
                            deployment_target=deployment_target
                        )
                    )
                    raise ParserError(
                        "Deployment target specific hook section "
                        f"'{deployment_target_hook_section}' contains an already "
                        "defined hook item!"
                    )

            hooks += deployment_target_hooks

        return hooks

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
                f"Value for section '{key}' should be a string, got {type(value).__name__}!"
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
