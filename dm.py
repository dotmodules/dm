import argparse
from pathlib import Path

from dotmodules.interpreter import CommandLineInterpreter
from dotmodules.modules.modules import ModuleError, Modules
from dotmodules.renderer import Renderer
from dotmodules.settings import Settings


def load_settings() -> Settings:
    parser = argparse.ArgumentParser(description="Dotmodules")

    parser.add_argument("--debug", type=int, required=True)
    parser.add_argument("--deployment-target", required=True)
    parser.add_argument("--relative-modules-path", type=Path, required=True)
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

    parsed_args = parser.parse_args()

    settings = Settings()
    settings.debug = bool(parsed_args.debug)
    settings.deployment_target = parsed_args.deployment_target
    settings.relative_modules_path = parsed_args.relative_modules_path
    settings.config_file_name = parsed_args.config_file_name
    settings.text_wrap_limit = parsed_args.text_wrap_limit
    settings.indent = parsed_args.indent
    settings.column_padding = parsed_args.column_padding
    settings.prompt_template = parsed_args.prompt_template
    settings.hotkey_exit = parsed_args.hotkey_exit
    settings.hotkey_help = parsed_args.hotkey_help
    settings.hotkey_hooks = parsed_args.hotkey_hooks
    settings.hotkey_modules = parsed_args.hotkey_modules
    settings.hotkey_variables = parsed_args.hotkey_variables
    settings.warning_wrapped_docs = bool(parsed_args.warning_wrapped_docs)

    return settings


def main() -> None:
    settings = load_settings()
    renderer = Renderer(settings=settings)

    try:
        modules = Modules(settings=settings)
    except ModuleError as e:
        renderer.empty_line()
        renderer.wrap.render(f"<<RED>>{e}<<RESET>>")
        return

    interpreter = CommandLineInterpreter(
        settings=settings, renderer=renderer, modules=modules
    )
    interpreter.run()


if __name__ == "__main__":
    main()
