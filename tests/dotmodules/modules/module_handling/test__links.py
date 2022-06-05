import os
from pathlib import Path

import pytest
from pytest_mock.plugin import MockerFixture

from dotmodules.modules.links import LinkError, LinkItem

# class TestLinkItemPathToFileHandling:
#     def test__full_path_calculation__file_exists(self, tmp_path: Path) -> None:
#         dummy_module_root = tmp_path

#         dummy_path_to_file = "./dummy.file"

#         dummy_full_path_to_file = dummy_module_root / dummy_path_to_file
#         dummy_full_path_to_file.touch()

#         dummy_path_to_symlink = "irrelevant"
#         dummy_name = "my_link"

#         link_item = LinkItem(
#             path_to_file=dummy_path_to_file,
#             path_to_symlink=dummy_path_to_symlink,
#             module_root=dummy_module_root,
#             name=dummy_name,
#         )

#         assert link_item.full_path_to_file == dummy_full_path_to_file

#     def test__full_path_calculation__file_non_existent(self, tmp_path: Path) -> None:
#         dummy_module_root = tmp_path

#         dummy_path_to_file = "./dummy.file"

#         # We are not touching the file here, so it won't be exist.

#         dummy_path_to_symlink = "irrelevant"
#         dummy_name = "my_link"

#         link_item = LinkItem(
#             path_to_file=dummy_path_to_file,
#             path_to_symlink=dummy_path_to_symlink,
#             module_root=dummy_module_root,
#             name=dummy_name,
#         )

#         with pytest.raises(LinkError) as error_context:
#             link_item.full_path_to_file

#         expected = "Link[my_link]: path_to_file './dummy.file' does not name a file!"
#         assert str(error_context.value) == expected


# class TestLinkItemPathToSymlinkHandling:
#     @pytest.mark.parametrize(
#         "home_literal",
#         [
#             LinkItem.HOME_LITERAL__STANDARD,
#             LinkItem.HOME_LITERAL__GUARDED,
#         ],
#     )
#     def test__full_path_calculation__home_directory_can_be_replaced(
#         self, tmp_path: Path, mocker: MockerFixture, home_literal: str
#     ) -> None:
#         dummy_module_root = tmp_path
#         mocker.patch(
#             "dotmodules.modules.links.Path.home", return_value=dummy_module_root
#         )

#         dummy_path_to_file = "irrelevant"
#         dummy_symlink_name = "dummy_link"
#         dummy_path_to_symlink = f"{home_literal}/{dummy_symlink_name}"
#         dummy_name = "my_link"

#         link_item = LinkItem(
#             path_to_file=dummy_path_to_file,
#             path_to_symlink=dummy_path_to_symlink,
#             module_root=dummy_module_root,
#             name=dummy_name,
#         )

#         expected_full_path_to_symlink = dummy_module_root / dummy_symlink_name
#         assert link_item.full_path_to_symlink == expected_full_path_to_symlink

#     def test__full_path_calculation__non_absolute__error(self, tmp_path: Path) -> None:
#         dummy_module_root = tmp_path
#         dummy_path_to_file = "irrelevant"
#         dummy_path_to_symlink = "./dummy.symlink"
#         dummy_name = "my_link"

#         link_item = LinkItem(
#             path_to_file=dummy_path_to_file,
#             path_to_symlink=dummy_path_to_symlink,
#             module_root=dummy_module_root,
#             name=dummy_name,
#         )

#         with pytest.raises(LinkError) as error_context:
#             link_item.full_path_to_symlink

#         expected = (
#             "Link[my_link]: path_to_file './dummy.symlink' should be an absolute path!"
#         )
#         assert str(error_context.value) == expected


# class TestLinkItemStatusCalculations:
#     def test__link_presence_can_be_calculated(
#         self, tmp_path: Path, mocker: MockerFixture
#     ) -> None:
#         dummy_module_root = tmp_path
#         mocker.patch(
#             "dotmodules.modules.links.Path.home", return_value=dummy_module_root
#         )

#         dummy_path_to_file = "./dummy_file"
#         dummy_path_to_symlink = f"$HOME/dummy_link"
#         dummy_name = "my_link"

#         (dummy_module_root / dummy_path_to_file).touch()

#         another_file = dummy_module_root / "another_file"
#         another_file.touch()

#         link_item = LinkItem(
#             path_to_file=dummy_path_to_file,
#             path_to_symlink=dummy_path_to_symlink,
#             module_root=dummy_module_root,
#             name=dummy_name,
#         )

#         # The link does not exist.
#         assert not link_item.link_exists
#         assert not link_item.target_matched
#         assert not link_item.deployed

#         # Another file gets linked with the same link.
#         os.symlink(src=another_file, dst=link_item.full_path_to_symlink)

#         assert link_item.link_exists
#         # For some reason mypy finds this line unreachable.. Probably due to the
#         # different assertions for the same variable, but it ignores the other
#         # variables :D
#         assert not link_item.target_matched  # type: ignore
#         assert not link_item.deployed

#         # Linking the target file but first removing the existing link.
#         link_item.full_path_to_symlink.unlink()
#         os.symlink(src=link_item.full_path_to_file, dst=link_item.full_path_to_symlink)

#         assert link_item.link_exists
#         assert link_item.target_matched
#         assert link_item.deployed
