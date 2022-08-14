import argparse
from pathlib import Path

from dotmodules.modules.variable_status import VariableStatusRefreshTask


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--transfer-file-path", type=Path, required=True)
    parsed_args = parser.parse_args()

    transfer_file_path = parsed_args.transfer_file_path

    VariableStatusRefreshTask.load_and_execute_from_transfer_file(
        transfer_file_path=transfer_file_path
    )


if __name__ == "__main__":
    main()
