import subprocess  # nosec B404
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class ShellAdapterError(Exception):
    pass


@dataclass
class ShellResult:
    command: List[str]
    cwd: Optional[Path]
    status_code: int
    stdout: List[str] = field(default_factory=list)
    stderr: List[str] = field(default_factory=list)


class ShellAdapter:
    """
    Adapter class that provides a simple interface for executing shell commands
    and get the output (standard output and standard error) in a sophisticated
    way.
    """

    @staticmethod
    def validate_command(command: List[str]) -> None:
        is_a_list = isinstance(command, list)
        is_a_list_of_strings = is_a_list and all(
            [isinstance(item, str) for item in command]
        )
        if not is_a_list or not is_a_list_of_strings:
            raise ShellAdapterError("passed command should be a list of strings")

    @classmethod
    def execute_and_capture(
        cls, command: List[str], cwd: Optional[Path] = None
    ) -> ShellResult:
        cls.validate_command(command=command)
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            shell=False,  # nosec B603
        )
        stdout, stderr = process.communicate()
        status_code = process.wait()

        result = ShellResult(
            command=command,
            cwd=cwd,
            status_code=status_code,
        )

        if stdout:
            for line in stdout.decode().splitlines():
                result.stdout.append(line)

        if stderr:
            for line in stderr.decode().splitlines():
                result.stderr.append(line)

        return result

    @classmethod
    def execute_interactively(
        cls, command: List[str], cwd: Optional[Path] = None
    ) -> int:
        cls.validate_command(command=command)
        try:
            status_code = subprocess.check_call(
                command, cwd=cwd, shell=False  # nosec B603
            )
        except subprocess.CalledProcessError as e:
            status_code = e.returncode
        return status_code
