#!/bin/sh

pwd

# shellcheck source=../../../utils/hooks/lib/logger.sh
. ../../../utils/hooks/lib/logger.sh

# shellcheck source=../../../utils/hooks/lib/execution.sh
. ../../../utils/hooks/lib/execution.sh

# shellcheck source=../../../utils/hooks/lib/linking.sh
. ../../../utils/hooks/lib/linking.sh

#==============================================================================
# CREATING PARENT DIRECTORIES
#==============================================================================

test__creating_parent_directory__parent_does_not_exist() {
  # Getting the test case level test directory.
  temp_dir="$3"
  symlink_parent="${temp_dir}/dir"
  path_to_symlink="${symlink_parent}/symlink"

  assert_no_directory "$symlink_parent"
  assert_no_file "$path_to_symlink"

  run _dm__symlink__create_parent_directory "$path_to_symlink"

  assert_directory "$symlink_parent"
  assert_no_file "$path_to_symlink"

  # There shouldn't be any content in the parent directory.
  run posix_adapter__find "$symlink_parent" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 0
}

test__creating_parent_directory_on_multiple_levels__parent_does_not_exist() {
  # Getting the test case level test directory.
  temp_dir="$3"
  symlink_parent="${temp_dir}/dir_1/dir_2/dir_3"
  path_to_symlink="${symlink_parent}/symlink"

  assert_no_directory "$symlink_parent"
  assert_no_file "$path_to_symlink"

  run _dm__symlink__create_parent_directory "$path_to_symlink"

  assert_directory "$symlink_parent"
  assert_no_file "$path_to_symlink"

  # There shouldn't be any content in the parent directory.
  run posix_adapter__find "$symlink_parent" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 0
}

test__creating_parent_directory__parent_exists() {
  # Getting the test case level test directory.
  temp_dir="$3"
  symlink_parent="${temp_dir}/dir"
  path_to_symlink="${symlink_parent}/symlink"
  posix_adapter__mkdir "$symlink_parent"

  assert_directory "$symlink_parent"
  assert_no_file "$path_to_symlink"

  run _dm__symlink__create_parent_directory "$path_to_symlink"

  assert_directory "$symlink_parent"
  assert_no_file "$path_to_symlink"

  # There shouldn't be any content in the parent directory.
  run posix_adapter__find "$symlink_parent" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 0
}

test__creating_parent_directory__insufficient_privileges() {
  # Getting the test case level test directory.
  temp_dir="$3"
  symlink_parent="${temp_dir}/dir"
  path_to_symlink="${symlink_parent}/symlink"

  # Mocking out the posix_adapter__mkdir adapter to check the failback elevated privileges
  # mode.
  posix_adapter__mkdir() {
    return 1
  }

  # Spying on the elevated privilege trigger.
  dm__execute_with_privilege() {
    posix_test__store__set 'execute_with_plivilege_params' "$*"
  }

  _dm__symlink__create_parent_directory "$path_to_symlink"

  # Elevated privilege execution should have been called.
  assert_equal \
    "$(posix_test__store__get 'execute_with_plivilege_params')" \
    "posix_adapter__mkdir --parents ${symlink_parent}"
}

#==============================================================================
# BACKING UP TARGETS
#==============================================================================

test__backup_creation__file() {
  # Getting the test case level test directory.
  temp_dir="$3"
  target="${temp_dir}/my_file"
  posix_adapter__touch "$target"

  # There should be only one file in the directory.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  # Mocking out the internal date call, to be able to generate a deterministic
  # backup file postfix.
  date() {
    echo 'timestamp'
  }

  _dm__symlink__backup_target "$target"

  # There should be only a single backuped file in the directory with the backup
  # prefix.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1
  assert_output_line_at_index 1 "${target}.backup_timestamp"
}

test__backup_creation__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"
  target="${temp_dir}/my_dir"
  posix_adapter__mkdir "$target"

  # There should be only one file in the directory.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  # Mocking out the internal date call, to be able to generate a deterministic
  # backup file postfix.
  date() {
    echo 'timestamp'
  }

  _dm__symlink__backup_target "$target"

  # There should be only a single backuped file in the directory with the backup
  # prefix.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1
  assert_output_line_at_index 1 "${target}.backup_timestamp"
}

test__backup_creation__insufficient_privileges() {
  # Getting the test case level test directory.
  temp_dir="$3"
  target="${temp_dir}/my_file"
  posix_adapter__touch "$target"

  # Mocking out the check if the user has sufficient enough permission to do the
  # backup.
  _dm__symlink__parent_of_target_is_writeable() {
    return 1
  }

  # Spying on the elevated privilege trigger by saving the arguments it is
  # called with.
  dm__execute_with_privilege() {
    posix_test__store__set 'execute_with_plivilege_params' "$*"
  }

  # Mocking out the internal date call, to be able to generate a deterministic
  # backup file postfix.
  date() {
    echo 'timestamp'
  }

  _dm__symlink__backup_target "$target"

  # Elevated privilege execution should have been called.
  assert_equal \
    "$(posix_test__store__get 'execute_with_plivilege_params')" \
    "mv ${target} ${target}.backup_timestamp"
}

#==============================================================================
# DELETING TARGETS
#==============================================================================

test__delete_target__file() {
  # Getting the test case level test directory.
  temp_dir="$3"
  target="${temp_dir}/my_file"
  posix_adapter__touch "$target"

  # There should be only one file in the directory.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  _dm__symlink__delete_target "$target"

  # There should be no file left.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 0
}

test__delete_target__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"
  target="${temp_dir}/my_directory"
  posix_adapter__mkdir "$target"

  # There should be only one file in the directory.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  _dm__symlink__delete_target "$target"

  # There should be no file left.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 0
}

test__delete_target__insufficient_privileges() {
  # Getting the test case level test directory.
  temp_dir="$3"
  target="${temp_dir}/my_file"
  posix_adapter__touch "$target"

  # Mocking out the check if the user has sufficient enough permission to do the
  # backup.
  posix_adapter__rm() {
    return 1
  }

  # Spying on the elevated privilege trigger by saving the arguments it is
  # called with.
  dm__execute_with_privilege() {
    posix_test__store__set 'execute_with_plivilege_params' "$*"
  }

  _dm__symlink__delete_target "$target"

  # Elevated privilege execution should have been called.
  assert_equal \
    "$(posix_test__store__get 'execute_with_plivilege_params')" \
    "posix_adapter__rm --force $target"
}

#==============================================================================
# LINKING TARGETS
#==============================================================================

test__create_symlink_helper__file() {
  # Getting the test case level test directory.
  temp_dir="$3"
  path_to_target="${temp_dir}/my_file"
  path_to_symlink="${temp_dir}/my_symlink"
  posix_adapter__touch "$path_to_target"

  _dm__symlink__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Symlink should have been created.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink_helper__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"
  path_to_target="${temp_dir}/my_dir"
  path_to_symlink="${temp_dir}/my_symlink"
  posix_adapter__mkdir "$path_to_target"

  _dm__symlink__create_symlink "$path_to_target" "$path_to_symlink"

  # Symlink should have been created.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink_helper__insufficient_privileges() {
  # Getting the test case level test directory.
  temp_dir="$3"
  path_to_target="${temp_dir}/my_file"
  path_to_symlink="${temp_dir}/my_symlink"
  posix_adapter__touch "$path_to_target"

  # Mocking out the check if the user has sufficient enough permission to do the
  # backup.
  _dm__symlink__parent_of_target_is_writeable() {
    return 1
  }

  # Spying on the elevated privilege trigger by saving the arguments it is
  # called with.
  dm__execute_with_privilege() {
    posix_test__store__set 'execute_with_plivilege_params' "$*"
  }

  _dm__symlink__create_symlink "$path_to_target" "$path_to_symlink"

  # Elevated privilege execution should have been called.
  assert_equal \
    "$(posix_test__store__get 'execute_with_plivilege_params')" \
    "posix_adapter__ln --symbolic --path-to-target ${path_to_target} --path-to-link ${path_to_symlink}"
}

#==============================================================================
# REMOVE SYMLINK
#==============================================================================

test__remove_symlink__symlink_exists() {
  # Getting the test case level test directory.
  temp_dir="$3"
  path_to_target="${temp_dir}/my_file"
  path_to_symlink="${temp_dir}/my_symlink"
  posix_adapter__touch "$path_to_target"
  posix_adapter__ln --symbolic --path-to-target "$path_to_target" --path-to-link "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Mocking out the user input.
  dm__logger__user_input() {
    # Setting the output variable to 'y'..
    dm_user_response='y'
  }

  dm__remove_symlink "$path_to_symlink"

  assert_no_symlink "$path_to_symlink"

  # Symlink should have been removed.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1
}

test__remove_symlink__symlink_does_not_exist() {
  # Getting the test case level test directory.
  temp_dir="$3"
  path_to_target="${temp_dir}/my_file"
  path_to_symlink="${temp_dir}/my_symlink"
  posix_adapter__touch "$path_to_target"

  assert_no_symlink "$path_to_symlink"

  dm__remove_symlink "$path_to_symlink"

  assert_no_symlink "$path_to_symlink"

  # Nothing shuldd have changed.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1
}

test__remove_symlink__user_abort() {
  # Getting the test case level test directory.
  temp_dir="$3"
  path_to_target="${temp_dir}/my_file"
  path_to_symlink="${temp_dir}/my_symlink"
  posix_adapter__touch "$path_to_target"
  posix_adapter__ln --symbolic --path-to-target "$path_to_target" --path-to-link "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Mocking out the user input.
  dm__logger__user_input() {
    # Setting the output variable to 'n' to abort the execution.
    dm_user_response='n'
  }

  dm__remove_symlink "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Nothing shuldd have changed.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2
}

#==============================================================================
# CREATE SYMLINK
#==============================================================================

test__create_symlink__fresh_start__file() {
  # Getting the test case level test directory.
  temp_dir="$3"
  path_to_target="${temp_dir}/my_file"
  path_to_symlink="${temp_dir}/my_symlink"
  posix_adapter__touch "$path_to_target"

  # There should only be the target file.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  assert_no_symlink "$path_to_symlink"

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Link should have been created.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink__fresh_start__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"
  path_to_target="${temp_dir}/my_dir"
  path_to_symlink="${temp_dir}/my_symlink"
  posix_adapter__mkdir "$path_to_target"

  # There should only be the target directory.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  assert_no_symlink "$path_to_symlink"

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Link should have been created.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink__same_link_already_exists__file() {
  # Getting the test case level test directory.
  temp_dir="$3"
  path_to_target="${temp_dir}/my_file"
  path_to_symlink="${temp_dir}/my_symlink"
  posix_adapter__touch "$path_to_target"
  posix_adapter__ln --symbolic --path-to-target "$path_to_target" --path-to-link "$path_to_symlink"

  # There should be the target file and the link itself.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Nothing should have been changed.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink__same_link_already_exists__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"
  path_to_target="${temp_dir}/my_dir"
  path_to_symlink="${temp_dir}/my_symlink"
  posix_adapter__mkdir "$path_to_target"
  posix_adapter__ln --symbolic --path-to-target "$path_to_target" --path-to-link "$path_to_symlink"

  # There should be the target directory and the link itself.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Nothing should have been changed.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink__link_already_exists_with_different_target__override__file() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_file"
  other_path_to_target="${temp_dir}/my_other_file"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__touch "$path_to_target"
  posix_adapter__ln --symbolic --path-to-target "$other_path_to_target" --path-to-link "$path_to_symlink"

  assert_file "$path_to_target"
  assert_symlink "$path_to_symlink"
  assert_symlink_target "$path_to_symlink" "$other_path_to_target"

  # Target and old link should be there.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='o'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Existing link should be overridden.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink__link_already_exists_with_different_target__backup__file() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_file"
  other_path_to_target="${temp_dir}/my_other_file"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__touch "$path_to_target"
  posix_adapter__ln --symbolic --path-to-target "$other_path_to_target" --path-to-link "$path_to_symlink"

  assert_file "$path_to_target"
  assert_symlink "$path_to_symlink"
  assert_symlink_target "$path_to_symlink" "$other_path_to_target"

  # Target and old link should be there.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='b'
  }

  # Mocking out the internal date call, to be able to generate a deterministic
  # backup file postfix.
  date() {
    echo 'timestamp'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  backed_up_symlink="${path_to_symlink}.backup_timestamp"
  assert_symlink "$path_to_symlink"
  assert_symlink "$backed_up_symlink"

  # Target, backed up old link and new link should be there.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 3

  assert_symlink_target "$path_to_symlink" "$path_to_target"
  assert_symlink_target "$backed_up_symlink" "$other_path_to_target"
}

test__create_symlink__link_already_exists_with_different_target__skip__file() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_file"
  other_path_to_target="${temp_dir}/my_other_file"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__touch "$path_to_target"
  posix_adapter__ln --symbolic --path-to-target "$other_path_to_target" --path-to-link "$path_to_symlink"

  assert_file "$path_to_target"
  assert_symlink "$path_to_symlink"
  assert_symlink_target "$path_to_symlink" "$other_path_to_target"

  # Target and old link should be there.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='s'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Target and old link should be only there.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_symlink_target "$path_to_symlink" "$other_path_to_target"
}

test__create_symlink__link_already_exists_with_different_target__override__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_dir"
  other_path_to_target="${temp_dir}/my_other_file"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__mkdir "$path_to_target"
  posix_adapter__ln --symbolic --path-to-target "$other_path_to_target" --path-to-link "$path_to_symlink"

  assert_directory "$path_to_target"
  assert_symlink "$path_to_symlink"
  assert_symlink_target "$path_to_symlink" "$other_path_to_target"

  # Target and old link should be there.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='o'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Existing link should be overridden.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink__link_already_exists_with_different_target__backup__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_dir"
  other_path_to_target="${temp_dir}/my_other_file"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__mkdir "$path_to_target"
  posix_adapter__ln --symbolic --path-to-target "$other_path_to_target" --path-to-link "$path_to_symlink"

  assert_directory "$path_to_target"
  assert_symlink "$path_to_symlink"
  assert_symlink_target "$path_to_symlink" "$other_path_to_target"

  # Target and old link should be there.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='b'
  }

  # Mocking out the internal date call, to be able to generate a deterministic
  # backup file postfix.
  date() {
    echo 'timestamp'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  backed_up_symlink="${path_to_symlink}.backup_timestamp"
  assert_symlink "$path_to_symlink"
  assert_symlink "$backed_up_symlink"

  # Target, backed up old link and new link should be there.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 3

  assert_symlink_target "$path_to_symlink" "$path_to_target"
  assert_symlink_target "$backed_up_symlink" "$other_path_to_target"
}

test__create_symlink__link_already_exists_with_different_target__skip__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_dir"
  other_path_to_target="${temp_dir}/my_other_file"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__mkdir "$path_to_target"
  posix_adapter__ln --symbolic --path-to-target "$other_path_to_target" --path-to-link "$path_to_symlink"

  assert_directory "$path_to_target"
  assert_symlink "$path_to_symlink"
  assert_symlink_target "$path_to_symlink" "$other_path_to_target"

  # Target and old link should be there.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2


  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='s'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # Target and old link should be only there.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_symlink_target "$path_to_symlink" "$other_path_to_target"
}

test__create_symlink__file_exists_in_place_of_symlink__override__file() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_file"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__touch "$path_to_symlink"

  assert_file "$path_to_symlink"

  # There should only the file in place of the link (the target file is nonexistent).
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='o'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # There should only be the created link (the target file is nonexistent).
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink__file_exists_in_place_of_symlink__backup__file() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_file"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__touch "$path_to_symlink"

  assert_file "$path_to_symlink"

  # There should only the file in place of the link (the target file is nonexistent).
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='b'
  }

  # Mocking out the internal date call, to be able to generate a deterministic
  # backup file postfix.
  date() {
    echo 'timestamp'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # There should only be the created link and the backed up file (the target file is nonexistent).
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_file "${path_to_symlink}.backup_timestamp"

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink__file_exists_in_place_of_symlink__skip__file() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_file"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__touch "$path_to_symlink"

  assert_file "$path_to_symlink"

  # There should only the file in place of the link (the target file is nonexistent).
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='s'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_file "$path_to_symlink"

  # Nothing should have been changed.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1
}

test__create_symlink__directory_exists_in_place_of_symlink__override__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_dir"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__mkdir "$path_to_symlink"

  assert_directory "$path_to_symlink"

  # There should only the file in place of the link (the target file is nonexistent).
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='o'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # There should only be the created link (the target file is nonexistent).
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink__directory_exists_in_place_of_symlink__backup__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_dir"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__mkdir "$path_to_symlink"

  assert_directory "$path_to_symlink"

  # There should only the file in place of the link (the target file is nonexistent).
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='b'
  }

  # Mocking out the internal date call, to be able to generate a deterministic
  # backup file postfix.
  date() {
    echo 'timestamp'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_symlink "$path_to_symlink"

  # There should only be the created link and the backed up file (the target file is nonexistent).
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 2

  assert_directory "${path_to_symlink}.backup_timestamp"

  assert_symlink_target "$path_to_symlink" "$path_to_target"
}

test__create_symlink__directory_exists_in_place_of_symlink__skip__directory() {
  # Getting the test case level test directory.
  temp_dir="$3"

  path_to_target="${temp_dir}/my_dir"
  path_to_symlink="${temp_dir}/my_symlink"

  posix_adapter__mkdir "$path_to_symlink"

  assert_directory "$path_to_symlink"

  # There should only the file in place of the link (the target file is nonexistent).
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1

  # Mocking out the user input.
  dm__logger__user_input() {
    dm_user_response='s'
  }

  dm__create_symlink "$path_to_target" "$path_to_symlink"

  assert_directory "$path_to_symlink"

  # Nothing should have been changed.
  run posix_adapter__find "$temp_dir" --min-depth 1 --max-depth 1
  assert_no_error
  assert_output_line_count 1
}