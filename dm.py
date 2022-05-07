from dotmodules.interpreter import CommandLineInterpreter


def main() -> None:
    interpreter = CommandLineInterpreter()
    interpreter.run()


if __name__ == "__main__":
    main()
