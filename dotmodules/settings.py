import argparse
import pathlib


def __parse_settins():
    parser = argparse.ArgumentParser(description="Dotmodules")
    parser.add_argument("--debug", type=int, required=True)
    parser.add_argument("--relative-modules-path", type=pathlib.Path, required=True)
    parser.add_argument("--config-file-name", type=str, required=True)
    parser.add_argument("--text-wrap-limit", type=int, required=True)
    parser.add_argument("--indent", type=int, required=True)
    parser.add_argument("--prompt-template", required=True)
    parser.add_argument("--hotkey-exit", required=True)
    parser.add_argument("--hotkey-help", required=True)
    parser.add_argument("--hotkey-hooks", required=True)
    parser.add_argument("--hotkey-modules", required=True)
    parser.add_argument("--hotkey-variables", required=True)
    parser.add_argument("--warning-wrapped-docs", type=int, required=True)
    return parser.parse_args()


settings = __parse_settins()
