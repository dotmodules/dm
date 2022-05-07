from pathlib import Path

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules import LinkItem


@pytest.fixture
def module_root() -> Path:
    return Path(__file__).parent / "link_testing_assets"


class TestLinkPathToFilePreparing:
    def test__full_path_to_file_can_be_resolved(self, module_root: Path) -> None:
        link = LinkItem(
            path_to_file="./dummy_file.txt",
            path_to_symlink="irrelevant for this test",
        )
        link.module_root = module_root

        assert link.full_path_to_file

    def test__non_existing__path_to_file__error(self, module_root: Path) -> None:
        link = LinkItem(
            path_to_file="./non_existent_file",
            path_to_symlink="irrelevant for this test",
        )
        link.module_root = module_root

        with pytest.raises(ValueError) as e:
            link.full_path_to_file
        expected = "Link.path_to_file does not name a file: './non_existent_file'"
        assert str(e.value) == expected


class TestLinkPathToSymlinkPreparing:
    def test__symlink_path_can_be_finalized(self, module_root: Path) -> None:
        link = LinkItem(
            path_to_file="irrelevant_for_this_test",
            path_to_symlink=str(module_root / "dummy_link"),
        )
        link.module_root = module_root
        assert link.full_path_to_symlink == module_root / "dummy_link"

    def test__home_directory_can_be_resolved_for_the_symlink_path(
        self, module_root: Path, mocker: MockerFixture
    ) -> None:
        mocker.patch("dotmodules.modules.Path.home", return_value=str(module_root))
        link = LinkItem(
            path_to_file="irrelevant_for_this_test",
            path_to_symlink="$HOME/dummy_link",
        )
        link.module_root = module_root
        assert link.full_path_to_symlink == module_root / "dummy_link"

    def test__symlink_path_should_be_absolute(self, module_root: Path) -> None:
        link = LinkItem(
            path_to_file="irrelevant_for_this_test",
            path_to_symlink="./not/absolute/path",
        )
        link.module_root = module_root
        with pytest.raises(ValueError) as e:
            link.full_path_to_symlink
        expected = (
            "Link.path_to_symlink should be an absolute path: './not/absolute/path'"
        )
        assert str(e.value) == expected


class TestLinkStatus:
    def test__nonexisting_link(self, module_root: Path) -> None:
        link = LinkItem(
            path_to_file="./dummy_file.txt",
            path_to_symlink=str(module_root / "nonexisting_link"),
        )
        link.module_root = module_root

        assert link.present is False
        assert link.target_matched is False

    def test__link_exists_but_different_target(self, module_root: Path) -> None:
        link = LinkItem(
            path_to_file="./dummy_file.txt",
            path_to_symlink=str(module_root / "other_link"),
        )
        link.module_root = module_root

        assert link.present is True
        assert link.target_matched is False

    def test__link_exists_and_target_matched(self, module_root: Path) -> None:
        link = LinkItem(
            path_to_file="./dummy_file.txt",
            path_to_symlink=str(module_root / "dummy_link"),
        )
        link.module_root = module_root

        assert link.present is True
        assert link.target_matched is True


class TestHookPathToFilePreparing:
    def test__full_path_to_file_can_be_resolved(self, module_root: Path) -> None:
        link = LinkItem(
            path_to_file="./dummy_file.txt", path_to_symlink="irrelevant for this test"
        )
        link.module_root = module_root

        assert link.full_path_to_file

    def test__non_existing__path_to_file__error(self, module_root: Path) -> None:
        link = LinkItem(
            path_to_file="./non_existent_file",
            path_to_symlink="irrelevant for this test",
        )
        link.module_root = module_root

        with pytest.raises(ValueError) as e:
            link.full_path_to_file
        expected = "Link.path_to_file does not name a file: './non_existent_file'"
        assert str(e.value) == expected
