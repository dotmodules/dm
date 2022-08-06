from pathlib import Path
from typing import Optional, cast

import pytest

from dotmodules.shell_adapter import ShellAdapter, ShellAdapterError


@pytest.fixture()
def test_root_path() -> Optional[Path]:
    return cast(Optional[Path], Path(__file__).parent)


class TestCommandValidation:
    def test__given_command_should_be_a_list(self) -> None:
        dummy_command = 42

        with pytest.raises(ShellAdapterError) as exception_info:
            # In this case we are calling the validator with the wrong type of argument..
            ShellAdapter.validate_command(command=dummy_command)  # type: ignore

        expected_message = "passed command should be a list of strings"
        assert exception_info.match(expected_message)

    def test__given_command_should_be_a_list_of_strings(self) -> None:
        dummy_command = ["I", "am", "not", "a", "string", 42, "!"]

        with pytest.raises(ShellAdapterError) as exception_info:
            # In this case we are calling the validator with the wrong type of argument..
            ShellAdapter.validate_command(command=dummy_command)  # type: ignore

        expected_message = "passed command should be a list of strings"
        assert exception_info.match(expected_message)


class TestGlobalCommandExecutionWithCapture:
    def test__capture_standard_output(self) -> None:
        dummy_command = ["echo", "hello"]
        result = ShellAdapter.execute_and_capture(command=dummy_command)

        assert result
        assert result.command == dummy_command
        assert not result.cwd
        assert result.status_code == 0
        assert result.stdout == ["hello"]
        assert result.stderr == []

    def test__capture_standard_error(self) -> None:
        dummy_command = ["cat", "invalid_file"]
        result = ShellAdapter.execute_and_capture(command=dummy_command)

        assert result
        assert result.command == dummy_command
        assert not result.cwd
        assert result.status_code == 1
        assert result.stdout == []
        assert len(result.stderr) > 0


class TestLocalScriptExecutionWithCapture:
    def test__capture_stdout__single_line(self, test_root_path: Optional[Path]) -> None:
        dummy_command = ["./dummy_command.sh", "--stdout", "hello"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute_and_capture(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 0
        assert result.stdout == ["hello"]
        assert result.stderr == []

    def test__capture_stdout__multiline(self, test_root_path: Optional[Path]) -> None:
        dummy_command = ["./dummy_command.sh"]
        dummy_command += ["--stdout", "line_1"]
        dummy_command += ["--stdout", "line_2"]
        dummy_command += ["--stdout", "line_3"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute_and_capture(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 0
        assert result.stdout == ["line_1", "line_2", "line_3"]
        assert result.stderr == []

    def test__capture_stderr__single_line(self, test_root_path: Optional[Path]) -> None:
        dummy_command = ["./dummy_command.sh", "--stderr", "hello"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute_and_capture(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 0
        assert result.stdout == []
        assert result.stderr == ["hello"]

    def test__capture_stderr__multiline(self, test_root_path: Optional[Path]) -> None:
        dummy_command = ["./dummy_command.sh"]
        dummy_command += ["--stderr", "line_1"]
        dummy_command += ["--stderr", "line_2"]
        dummy_command += ["--stderr", "line_3"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute_and_capture(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 0
        assert result.stdout == []
        assert result.stderr == ["line_1", "line_2", "line_3"]

    def test__capture_status_code(self, test_root_path: Optional[Path]) -> None:
        dummy_command = ["./dummy_command.sh", "--status", "42"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute_and_capture(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 42
        assert result.stdout == []
        assert result.stderr == []

    def test__combined_case(self, test_root_path: Optional[Path]) -> None:
        dummy_command = ["./dummy_command.sh"]
        dummy_command += ["--stdout", "stdout_line_1"]
        dummy_command += ["--stdout", "stdout_line_2"]
        dummy_command += ["--stderr", "stderr_line_1"]
        dummy_command += ["--stderr", "stderr_line_2"]
        dummy_command += ["--status", "42"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute_and_capture(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 42
        assert result.stdout == ["stdout_line_1", "stdout_line_2"]
        assert result.stderr == ["stderr_line_1", "stderr_line_2"]


class TestExecuteInteractively:
    def test__global_command__normal_execution(
        self, test_root_path: Optional[Path]
    ) -> None:
        dummy_command = ["echo", "hello"]
        dummy_cwd = test_root_path
        status_code = ShellAdapter.execute_interactively(
            command=dummy_command, cwd=dummy_cwd
        )

        assert status_code == 0

    def test__local_script__error(self, test_root_path: Optional[Path]) -> None:
        dummy_command = ["cat", "invalid_file"]
        dummy_cwd = test_root_path
        status_code = ShellAdapter.execute_interactively(
            command=dummy_command, cwd=dummy_cwd
        )

        assert status_code == 1

    def test__local_script__normal_execution(
        self, test_root_path: Optional[Path]
    ) -> None:
        dummy_command = ["./dummy_command.sh", "--stdout", "hello"]
        dummy_cwd = test_root_path
        status_code = ShellAdapter.execute_interactively(
            command=dummy_command, cwd=dummy_cwd
        )

        assert status_code == 0

    def test__local_script__valid(self, test_root_path: Optional[Path]) -> None:
        dummy_command = ["./dummy_command.sh", "--status", "42"]
        dummy_cwd = test_root_path
        status_code = ShellAdapter.execute_interactively(
            command=dummy_command, cwd=dummy_cwd
        )

        assert status_code == 42
