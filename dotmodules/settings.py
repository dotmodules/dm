from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    """
    Transfer only dataclass that does not perform any checking on the passed
    values. The validation is performed by the argparse module. All fields set
    to be assignable after the initialization.
    """

    # The relative modules path has to be set explicitly.
    relative_modules_path: Optional[Path] = None

    # Core settings
    debug: bool = False
    deployment_target: str = ""
    config_file_name: str = "dm.toml"

    # UI settings
    text_wrap_limit: int = 90
    indent: int = 2
    column_padding: int = 2
    prompt_template: str = "<<SPACE>><<BOLD>>dm<<RESET>><<SPACE>>#<<SPACE>>"
    hotkey_exit: str = "q|quit|exit"
    hotkey_help: str = "help"
    hotkey_hooks: str = "h|hooks"
    hotkey_modules: str = "m|modules"
    hotkey_variables: str = "v|variables"
    warning_wrapped_docs: bool = True
    header_width: int = 10
    header_separator: int = 2

    @property
    def dm_cache_root(self) -> Path:
        """
        The current working directory is the dm repository root for the
        following path definitions.
        """
        return (Path.cwd() / ".dm_cache").resolve()

    @property
    def dm_cache_variables(self) -> Path:
        return self.dm_cache_root / "variables"

    @property
    def dm_cache_variable_status_hooks(self) -> Path:
        return self.dm_cache_root / "variable_status_workers"

    @property
    def body_width(self) -> int:
        return self.text_wrap_limit - self.header_width - self.column_padding

    @property
    def rendered_indent(self) -> str:
        return " " * self.indent

    @property
    def rendered_column_padding(self) -> str:
        return " " * self.column_padding

    @property
    def rendered_header_separator(self) -> str:
        return " " * self.header_separator
