from typing import Dict, List, Optional

RawSimpleConfigDataType = str
RawBooleanConfigDataType = bool
RawVariablesConfigDataType = Dict[str, str | List[str]]
RawObjectListConfigDataType = List[Dict[str, str | int]]
RawCommonConfigDataType = Dict[
    str,
    Optional[
        RawSimpleConfigDataType
        | RawBooleanConfigDataType
        | RawVariablesConfigDataType
        | RawObjectListConfigDataType
    ],
]
ParsedVariablesConfigDataType = Dict[str, List[str]]


class ConfigParser:
    """
    Inner class that can be used to parse, condition and validate the raw
    configuration files.
    """

    KEY__NAME = "name"
    KEY__VERSION = "version"
    KEY__ENABLED = "enabled"
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
    def parse_enabled(cls, data: RawCommonConfigDataType) -> bool:
        return cls._parse_boolean(data=data, key=cls.KEY__ENABLED)

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
    def parse_links(cls, data: RawCommonConfigDataType) -> List[LinkItem]:
        links = cast(
            List[LinkItem],
            cls._parse_item_list(data=data, key=cls.KEY__LINKS, item_class=LinkItem),
        )
        return links

    @classmethod
    def parse_hooks(cls, data: RawCommonConfigDataType) -> List[ShellScriptHook]:
        hooks = cast(
            List[ShellScriptHook],
            cls._parse_item_list(
                data=data, key=cls.KEY__HOOKS, item_class=ShellScriptHook
            ),
        )
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
    def _parse_boolean(
        cls, data: RawCommonConfigDataType, key: str, mandatory: bool = True
    ) -> bool:
        if key not in data:
            if not mandatory:
                return False
            raise SyntaxError(f"mandatory '{key}' section is missing")
        value = data[key]
        value = cast(RawBooleanConfigDataType, value)
        if not isinstance(value, bool):
            raise ValueError(f"value for section '{key}' should be a boolean")
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
