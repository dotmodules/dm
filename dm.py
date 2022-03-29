import sys

from dotmodules.settings import load_settings

if __name__ == "__main__":
    args = sys.argv[1:]
    load_settings(args=args)

    from dotmodules.interpreter import CommandLineInterpreter

    interpreter = CommandLineInterpreter()
    interpreter.run()
