from dotmodules.modules import Modules
from dotmodules.settings import settings


class CommandLineInterpreter:
    def run(self):
        _ = Modules.load(
            modules_root_path=settings.relative_modules_path,
            config_file_name=settings.config_file_name,
        )
        while True:
            raw_command = input("hello> ")
            print(settings)
            if raw_command.startswith("q"):
                break
