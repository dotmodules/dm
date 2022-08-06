import argparse
import pathlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Settings:
    """
    Transfer only dataclass that does not perform any checking on the passed
    values. The validation is performed by the argparse module. All fields set
    to be assignable after the initialization.
    """

    debug: bool = field(init=False)
    deployment_target: str = field(init=False)
    relative_modules_path: pathlib.Path = field(init=False)
    config_file_name: str = field(init=False)
    text_wrap_limit: int = field(init=False)
    indent: str = field(init=False)
    column_padding: str = field(init=False)
    prompt_template: str = field(init=False)
    hotkey_exit: str = field(init=False)
    hotkey_help: str = field(init=False)
    hotkey_hooks: str = field(init=False)
    hotkey_modules: str = field(init=False)
    hotkey_variables: str = field(init=False)
    warning_wrapped_docs: bool = field(init=False)

    # The current working directory is the dm repository root for the following
    # path definitions.
    dm_cache_root: Path = (Path.cwd() / ".dm_cache").resolve()
    dm_cache_variables: Path = (Path.cwd() / ".dm_cache" / "variables").resolve()
    header_width: int = 10
    header_separator: str = "  "

    @property
    def body_width(self) -> int:
        return self.text_wrap_limit - self.header_width - len(self.column_padding)


def _get_argument_list() -> List[str]:
    # The argparse module cannot handle the pure sys.argv input. It expects to
    # receive only the parseable parameters in the input list.
    return sys.argv[1:]


def load_settings() -> Settings:
    parser = argparse.ArgumentParser(description="Dotmodules")

    parser.add_argument("--debug", type=int, required=True)
    parser.add_argument("--deployment-target", required=True)
    parser.add_argument("--relative-modules-path", type=pathlib.Path, required=True)
    parser.add_argument("--config-file-name", type=str, required=True)
    parser.add_argument("--text-wrap-limit", type=int, required=True)
    parser.add_argument("--indent", type=int, required=True)
    parser.add_argument("--column-padding", type=int, required=True)
    parser.add_argument("--prompt-template", required=True)
    parser.add_argument("--hotkey-exit", required=True)
    parser.add_argument("--hotkey-help", required=True)
    parser.add_argument("--hotkey-hooks", required=True)
    parser.add_argument("--hotkey-modules", required=True)
    parser.add_argument("--hotkey-variables", required=True)
    parser.add_argument("--warning-wrapped-docs", type=int, required=True)

    args = _get_argument_list()
    parsed_args = parser.parse_args(args)

    settings = Settings()
    settings.debug = bool(parsed_args.debug)
    settings.deployment_target = parsed_args.deployment_target
    settings.relative_modules_path = parsed_args.relative_modules_path
    settings.config_file_name = parsed_args.config_file_name
    settings.text_wrap_limit = parsed_args.text_wrap_limit
    settings.indent = " " * parsed_args.indent
    settings.column_padding = " " * parsed_args.column_padding
    settings.prompt_template = parsed_args.prompt_template
    settings.hotkey_exit = parsed_args.hotkey_exit
    settings.hotkey_help = parsed_args.hotkey_help
    settings.hotkey_hooks = parsed_args.hotkey_hooks
    settings.hotkey_modules = parsed_args.hotkey_modules
    settings.hotkey_variables = parsed_args.hotkey_variables
    settings.warning_wrapped_docs = bool(parsed_args.warning_wrapped_docs)

    return settings
