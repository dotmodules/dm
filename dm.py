import os

from dotmodules.modules import Modules
from dotmodules.settings import settings



class CommandLineInterpreter:
    def run(self):
        while True:
            raw_command = input("hello> ")
            if raw_command.startswith("q"):
                break


def main():
    modules = Modules.load(
        modules_root_path=settings.relative_modules_path,
        config_file_name=settings.config_file_name,
    )

    interpreter = CommandLineInterpreter()
    interpreter.run()


if __name__ == "__main__":
    main()
