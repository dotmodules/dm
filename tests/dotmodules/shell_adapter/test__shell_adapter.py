from pathlib import Path

import pytest

from dotmodules.shell_adapter import ShellAdapter, ShellAdapterError


@pytest.fixture()
def test_root_path():
    return str(Path(__file__).parent)


class TestGlobalCommandExecution:
    def test__capture_standard_output(self):
        dummy_command = ["echo", "hello"]
        result = ShellAdapter.execute(command=dummy_command)

        assert result
        assert result.command == dummy_command
        assert not result.cwd
        assert result.status_code == 0
        assert result.stdout == ["hello"]
        assert result.stderr == []

    def test__capture_standard_error(self):
        dummy_command = ["cat", "invalid_file"]
        result = ShellAdapter.execute(command=dummy_command)

        assert result
        assert result.command == dummy_command
        assert not result.cwd
        assert result.status_code == 1
        assert result.stdout == []
        assert len(result.stderr) > 0


class TestLocalScriptExecution:
    def test__capture_stdout__single_line(self, test_root_path):
        dummy_command = ["./dummy_command.sh", "--stdout", "hello"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 0
        assert result.stdout == ["hello"]
        assert result.stderr == []

    def test__capture_stdout__multiline(self, test_root_path):
        dummy_command = ["./dummy_command.sh"]
        dummy_command += ["--stdout", "line_1"]
        dummy_command += ["--stdout", "line_2"]
        dummy_command += ["--stdout", "line_3"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 0
        assert result.stdout == ["line_1", "line_2", "line_3"]
        assert result.stderr == []

    def test__capture_stderr__single_line(self, test_root_path):
        dummy_command = ["./dummy_command.sh", "--stderr", "hello"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 0
        assert result.stdout == []
        assert result.stderr == ["hello"]

    def test__capture_stderr__multiline(self, test_root_path):
        dummy_command = ["./dummy_command.sh"]
        dummy_command += ["--stderr", "line_1"]
        dummy_command += ["--stderr", "line_2"]
        dummy_command += ["--stderr", "line_3"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 0
        assert result.stdout == []
        assert result.stderr == ["line_1", "line_2", "line_3"]

    def test__capture_status_code(self, test_root_path):
        dummy_command = ["./dummy_command.sh", "--status", "42"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 42
        assert result.stdout == []
        assert result.stderr == []

    def test__combined_case(self, test_root_path):
        dummy_command = ["./dummy_command.sh"]
        dummy_command += ["--stdout", "stdout_line_1"]
        dummy_command += ["--stdout", "stdout_line_2"]
        dummy_command += ["--stderr", "stderr_line_1"]
        dummy_command += ["--stderr", "stderr_line_2"]
        dummy_command += ["--status", "42"]
        dummy_cwd = test_root_path
        result = ShellAdapter.execute(command=dummy_command, cwd=dummy_cwd)

        assert result
        assert result.command == dummy_command
        assert result.cwd == dummy_cwd
        assert result.status_code == 42
        assert result.stdout == ["stdout_line_1", "stdout_line_2"]
        assert result.stderr == ["stderr_line_1", "stderr_line_2"]


class TestCommandValidation:
    def test__given_command_should_be_a_list(self):
        dummy_command = 42

        with pytest.raises(ShellAdapterError) as exception_info:
            ShellAdapter.validate_command(command=dummy_command)

        expected_message = "passed command should be a list of strings"
        assert str(exception_info.value) == expected_message

    def test__given_command_should_be_a_list_of_strings(self):
        dummy_command = ["I", "am", "not", "a", "string", 42, "!"]

        with pytest.raises(ShellAdapterError) as exception_info:
            ShellAdapter.validate_command(command=dummy_command)

        expected_message = "passed command should be a list of strings"
        assert str(exception_info.value) == expected_message
