import os
from pathlib import Path

from pytest_mock.plugin import MockerFixture

from dotmodules.modules.links import LinkItem
from dotmodules.modules.path import PathManager


class TestLinkErrorReportingCases:
    def test__path_to_file_exists__no_errors(self, tmp_path: Path) -> None:
        dummy_module_root = tmp_path

        dummy_path_to_file = "./dummy.file"

        dummy_full_path_to_file = dummy_module_root / dummy_path_to_file
        dummy_full_path_to_file.touch()

        dummy_path_to_symlink = "irrelevant"
        dummy_name = "my_link"

        link_item = LinkItem(
            path_to_file=dummy_path_to_file,
            path_to_symlink=dummy_path_to_symlink,
            name=dummy_name,
        )

        path_manager = PathManager(root_path=dummy_module_root)

        assert link_item.report_errors(path_manager=path_manager) == []

    def test__path_to_file_does_not_exists__errors_should_be_reported(
        self, tmp_path: Path
    ) -> None:
        dummy_module_root = tmp_path

        dummy_path_to_file = "./dummy.file"

        # NOTE: We are not touching the file here, so it won't be exist.

        dummy_path_to_symlink = "irrelevant"
        dummy_name = "my_link"

        link_item = LinkItem(
            path_to_file=dummy_path_to_file,
            path_to_symlink=dummy_path_to_symlink,
            name=dummy_name,
        )

        path_manager = PathManager(root_path=dummy_module_root)

        expected_errors = [
            f"Link[{dummy_name}]: path_to_file '{dummy_path_to_file}' does not name a file!",
        ]
        assert link_item.report_errors(path_manager=path_manager) == expected_errors


class TestLinkItemStatusCalculations:
    def test__link_presence_can_be_calculated(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        dummy_module_root = tmp_path
        # Modifying the PathManager class to resolve the $HOME literal to the
        # tmp_path.
        mocker.patch(
            "dotmodules.modules.path.Path.home", return_value=dummy_module_root
        )

        dummy_path_to_file = "./dummy_file"
        dummy_path_to_symlink = "$HOME/dummy_link"
        dummy_name = "my_link"

        (dummy_module_root / dummy_path_to_file).touch()

        another_file = dummy_module_root / "another_file"
        another_file.touch()

        link_item = LinkItem(
            path_to_file=dummy_path_to_file,
            path_to_symlink=dummy_path_to_symlink,
            name=dummy_name,
        )

        path_manager = PathManager(root_path=dummy_module_root)

        full_path_to_file = path_manager.resolve_local_path(link_item.path_to_file)
        full_path_to_symlink = path_manager.resolve_absolute_path(
            link_item.path_to_symlink
        )

        # The link does not exist.
        assert not link_item.check_if_link_exists(path_manager=path_manager)
        assert not link_item.check_if_target_matched(path_manager=path_manager)

        # Another file gets linked with the same link.
        os.symlink(src=another_file, dst=full_path_to_symlink)

        assert link_item.check_if_link_exists(path_manager=path_manager)
        assert not link_item.check_if_target_matched(path_manager=path_manager)

        # Linking the target file but first removing the existing link.
        full_path_to_symlink.unlink()
        os.symlink(src=full_path_to_file, dst=full_path_to_symlink)

        assert link_item.check_if_link_exists(path_manager=path_manager)
        assert link_item.check_if_target_matched(path_manager=path_manager)
