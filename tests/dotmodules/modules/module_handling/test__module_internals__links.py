from pathlib import Path

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules import LinkItem, Module


@pytest.fixture
def module() -> Module:
    module = Module(
        name="dummy_module",
        version="dummy_version",
        enabled=True,
        documentation=[""],
        variables={},
        root=Path(__file__).parent / "link_testing_assets",
    )
    return module


class TestLinkPathToFilePreparing:
    def test__full_path_to_file_can_be_resolved(self, module: Module) -> None:
        link = LinkItem(
            path_to_file="./dummy_file.txt",
            path_to_symlink="irrelevant for this test",
        )
        module.add_link(link=link)

        assert link.full_path_to_file

    def test__non_existing__path_to_file__error(self, module: Module) -> None:
        link = LinkItem(
            path_to_file="./non_existent_file",
            path_to_symlink="irrelevant for this test",
        )
        module.add_link(link=link)

        with pytest.raises(ValueError) as e:
            link.full_path_to_file
        expected = "Link.path_to_file does not name a file: './non_existent_file'"
        assert str(e.value) == expected


class TestLinkPathToSymlinkPreparing:
    def test__symlink_path_can_be_finalized(self, module: Module) -> None:
        link = LinkItem(
            path_to_file="irrelevant_for_this_test",
            path_to_symlink=str(module.root / "dummy_link"),
        )
        module.add_link(link=link)
        assert link.full_path_to_symlink == module.root / "dummy_link"

    def test__home_directory_can_be_resolved_for_the_symlink_path(
        self, module: Module, mocker: MockerFixture
    ) -> None:
        mocker.patch("dotmodules.modules.Path.home", return_value=str(module.root))
        link = LinkItem(
            path_to_file="irrelevant_for_this_test",
            path_to_symlink="$HOME/dummy_link",
        )
        module.add_link(link=link)
        assert link.full_path_to_symlink == module.root / "dummy_link"

    def test__symlink_path_should_be_absolute(self, module: Module) -> None:
        link = LinkItem(
            path_to_file="irrelevant_for_this_test",
            path_to_symlink="./not/absolute/path",
        )
        module.add_link(link=link)
        with pytest.raises(ValueError) as e:
            link.full_path_to_symlink
        expected = (
            "Link.path_to_symlink should be an absolute path: './not/absolute/path'"
        )
        assert str(e.value) == expected


class TestLinkStatus:
    def test__nonexisting_link(self, module: Module) -> None:
        link = LinkItem(
            path_to_file="./dummy_file.txt",
            path_to_symlink=str(module.root / "nonexisting_link"),
        )
        module.add_link(link=link)

        assert link.present is False
        assert link.target_matched is False

    def test__link_exists_but_different_target(self, module: Module) -> None:
        link = LinkItem(
            path_to_file="./dummy_file.txt",
            path_to_symlink=str(module.root / "other_link"),
        )
        module.add_link(link=link)

        assert link.present is True
        assert link.target_matched is False

    def test__link_exists_and_target_matched(self, module: Module) -> None:
        link = LinkItem(
            path_to_file="./dummy_file.txt",
            path_to_symlink=str(module.root / "dummy_link"),
        )
        module.add_link(link=link)

        assert link.present is True
        assert link.target_matched is True


class TestHookPathToFilePreparing:
    def test__full_path_to_file_can_be_resolved(self, module: Module) -> None:
        link = LinkItem(
            path_to_file="./dummy_file.txt", path_to_symlink="irrelevant for this test"
        )
        module.add_link(link=link)

        assert link.full_path_to_file

    def test__non_existing__path_to_file__error(self, module: Module) -> None:
        link = LinkItem(
            path_to_file="./non_existent_file",
            path_to_symlink="irrelevant for this test",
        )
        module.add_link(link=link)

        with pytest.raises(ValueError) as e:
            link.full_path_to_file
        expected = "Link.path_to_file does not name a file: './non_existent_file'"
        assert str(e.value) == expected
