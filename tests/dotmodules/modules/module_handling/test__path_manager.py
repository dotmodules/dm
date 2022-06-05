import os
from pathlib import Path

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.path import PathManager


@pytest.fixture
def path_manager(tmp_path) -> PathManager:
    return PathManager(root_path=tmp_path)


class TestLocalPathResolvingCases:
    def test__local_path_can_be_resolved__as_string(
        self, path_manager: PathManager
    ) -> None:
        local_path = "./local_path"
        expected = path_manager.root_path / "local_path"

        result = path_manager.resolve_local_path(str(local_path))

        assert result == expected

    def test__local_path_can_be_resolved__as_path(
        self, path_manager: PathManager
    ) -> None:
        local_path = Path("./local_path")
        expected = path_manager.root_path / "local_path"

        result = path_manager.resolve_local_path(local_path)

        assert result == expected


class TestAbsolutePathResolvingCases:
    def test__absolute_path_can_be_resolved_for_file_name(
        self, path_manager: PathManager
    ) -> None:
        dummy_file = path_manager.root_path / "my_file"
        old_cwd = os.getcwd()
        os.chdir(path_manager.root_path)
        # Would be resolved as a file in the root path.
        result = path_manager.resolve_absolute_path("./my_file")
        assert result == dummy_file
        os.chdir(old_cwd)

    @pytest.mark.parametrize(
        "home_literal",
        [
            PathManager.HOME_LITERAL__STANDARD,
            PathManager.HOME_LITERAL__GUARDED,
        ],
    )
    def test__standard_home_literal_can_be_resolved(
        self, path_manager: PathManager, home_literal: str, mocker: MockerFixture
    ) -> None:
        dummy_home = Path("/my_home")
        mocker.patch("dotmodules.modules.path.Path.home", return_value=dummy_home)
        expected = dummy_home / "my_file"
        result = path_manager.resolve_absolute_path(f"{home_literal}/my_file")
        assert result == expected


class TestRelativePathCases:
    def test__relative_path_can_be_calculated__case_1(
        self, path_manager: PathManager
    ) -> None:
        from_path = path_manager.root_path
        to_path = from_path / "dir_1" / "dir_2"
        expected = Path("dir_1/dir_2")
        result = path_manager.get_relative_path(from_path=from_path, to_path=to_path)
        assert result == expected

    def test__relative_path_can_be_calculated__case_2(
        self, path_manager: PathManager
    ) -> None:
        from_path = path_manager.root_path / "dir_1" / "dir_2"
        to_path = path_manager.root_path
        expected = Path("../..")
        result = path_manager.get_relative_path(from_path=from_path, to_path=to_path)
        assert result == expected
