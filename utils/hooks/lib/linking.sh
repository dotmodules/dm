#!/bin/sh

#==============================================================================
# SANE ENVIRONMENT
#==============================================================================

set -e  # exit on error
set -u  # prevent unset variable expansion

#==============================================================================
# PATH HANDLING
#==============================================================================

# Changing the path is unnecesary for this script. It will be sourced by another
# script that has the relative path prefix for the dotmodules repository root.

#==============================================================================
# LINK MANAGEMENT
#==============================================================================

#==============================================================================
# Function that attempts to create a symlink in the targeted path for the given
# file.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] path_to_target - Absolute path to the linkable file or directory.
#   [2] path_to_symlink - Absolute path to the creatable symlink.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Displays the inner workings via the logger interface.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__create_symlink() {
  ___path_to_target="$1"
  ___path_to_symlink="$2"

  dm__logger__task "${BOLD}Linking symlink..${RESET}"
  dm__logger__log "Path to target:  ${UNDERLINE}${___path_to_target}${RESET}"
  dm__logger__log "Path to symlink: ${UNDERLINE}${___path_to_symlink}${RESET}"

  # If there is something at the symlinks's path.
  # NOTE: We have to have here two checks as test resolves symlinks during the
  # '-e' check. If the symlink already exist with a non existing target, the
  # check would fail, hence the additional '-L' check to cover this case..
  if [ -e "$___path_to_symlink" ] || [ -L "$___path_to_symlink" ]
  then

    dm__logger__separator
    ___existing_target="$(posix_adapter__readlink --canonicalize "$___path_to_symlink")"

    if [ -L "$___path_to_symlink" ]
    then
      if [ "$___path_to_target" = "$___existing_target" ]
      then
        dm__logger__success "${BOLD}Required symlink already exists. Nothing to do.${RESET}"
        return 0
      else
        dm__logger__warning "${BOLD}${YELLOW}Symlink already exists with a different target!${RESET}"
      fi

    elif [ -f "$___path_to_symlink" ]
    then
      dm__logger__warning "${BOLD}${YELLOW}A file already exists in the same path!${RESET}"

    elif [ -d "$___path_to_symlink" ]
    then
      dm__logger__warning "${BOLD}${YELLOW}A direcotry already exists in the same path!${RESET}"

    fi

    dm__logger__log "${YELLOW}Existing target: ${UNDERLINE}${___existing_target}${RESET}"
    dm__logger__log "${YELLOW}You have several options to resolve the situation:${RESET}"
    dm__logger__log " ${YELLOW}- ${BOLD}[o]${RESET} ${YELLOW}override${RESET}"
    dm__logger__log " ${YELLOW}- ${BOLD}[b]${RESET} ${YELLOW}backup${RESET}"
    dm__logger__log " ${YELLOW}- ${BOLD}[s]${RESET} ${YELLOW}skip${RESET}"

    while :
    do
      dm__logger__user_input "${YELLOW}What do you want to do? ${BOLD}[o|b|s]${RESET}"
      case "$dm_user_response" in
        o)
          # Removing the existing symlink to be able to create the new one.
          _dm__symlink__delete_target "$___path_to_symlink"
          dm__logger__log "${YELLOW}Existing symlink removed${RESET}"
          dm__logger__separator
          break
          ;;
        b)
          # Backing up the existing symlink.
          _dm__symlink__backup_target "$___path_to_symlink"
          dm__logger__separator
          break
          ;;
        s)
          # Skipping the linking of the current symlink.
          dm__logger__separator
          dm__logger__success "${BOLD}Skipped linking for the current target link${RESET}"
          return 0
          ;;
        *)
          ;;
      esac
    done
  else
    _dm__symlink__create_parent_directory "$___path_to_symlink"
  fi

  _dm__symlink__create_symlink "$___path_to_target" "$___path_to_symlink"

  dm__logger__success "${BOLD}Symlink created${RESET}"
}

#==============================================================================
# Makes sure that the parent directories are present for the passed symlink
# path. It will ask for elevated privileges if needed.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] path_to_symlink - Absolute path to the creatable symlink.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Asks for elevated privileges if needed.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
_dm__symlink__create_parent_directory() {
  ___target_path="$1"
  ___parent_dir="$(posix_adapter__dirname "$___target_path")"

  dm__logger__info "Creating the parent directory of the symlink.."

  if [ -d "$___parent_dir" ]
  then
    dm__logger__log "Directory already exists"
    return 0
  fi
  if posix_adapter__mkdir --parents "$___parent_dir"
  then
    :
  else
    dm__logger__warning "You don't have sufficient enough privileges to prepare the symlink's directory.."
    dm__execute_with_privilege posix_adapter__mkdir --parents "$___parent_dir"
  fi

  dm__logger__log "Symlink parent directory created"
}

#==============================================================================
# Creates a backup for the given path by moving it to another file. It will ask
# for elevated privileges if needed.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] path_to_target - Absolute path to the backupable target file/directory.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Asks for elevated privileges if needed.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
_dm__symlink__backup_target() {
  ___backup_target="$1"
  ___backup_path="${___backup_target}.backup_$(date +"%s")"

  dm__logger__info "${YELLOW}Backing up the existing file..${RESET}"

  if _dm__symlink__parent_of_target_is_writeable "$___backup_path"
  then
    mv "$___backup_target" "$___backup_path"
  else
    dm__logger__warning "${YELLOW}You don't have sufficient enough privileges to backup the existing file..${RESET}"
    dm__execute_with_privilege mv "$___backup_target" "$___backup_path"
  fi

  dm__logger__log " ${YELLOW}Existing file backed up: ${UNDERLINE}${___backup_path}${RESET}"
}

#==============================================================================
# Removes the existing symlink. It will ask for elevated privileges if needed.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] path_to_target - Absolute path to the deletable symlink.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Asks for elevated privileges if needed.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
_dm__symlink__delete_target() {
  ___delete_target="$1"

  dm__logger__info "${YELLOW}Removing the existing target..${RESET}"

  if posix_adapter__rm --force --recursive "$___delete_target"
  then
    :
  else
    dm__logger__warning "${YELLOW}You don't have sufficient enough privileges to delete the existing target..${RESET}"
    dm__execute_with_privilege posix_adapter__rm --force "$___delete_target"
  fi
}

#==============================================================================
# Checks whether the given target path would be writeable by the current user.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] checking_path - Path that should be checked.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   None
# STDERR:
#   None
# Status:
#   0 - The current user would be able to write the checking path.
#   1 - The current user would not be able to write the checking path.
#==============================================================================
_dm__symlink__target_is_writeable() {
  ___checking_path="$1"
  # The '-w' flag here means: FILE exists and the user has write access
  test -w "$___checking_path"
}

#==============================================================================
# Checks whether the given target path would be writeable by the current user by
# checking if the parent directory has sufficient priviledges.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] checking_path - Path that should be checked.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   None
# STDERR:
#   None
# Status:
#   0 - The current user would be able to write the parent of the given
#       file/directory.
#   1 - The current user would not be able to write the parent of the given
#       file/directory.
#==============================================================================
_dm__symlink__parent_of_target_is_writeable() {
  ___checking_path="$1"
  # The '-w' flag here means: FILE exists and the user has write access
  test -w "$(posix_adapter__dirname "$___checking_path")"
}

#==============================================================================
# Creates the symlink for the given file path. It will ask for elevated
# privileges if needed.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] target_path - Absolute path to the linkable file or directory.
#   [2] symlink_path - Absolute path to the creatable symlink.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Asks for elevated privileges if needed.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
_dm__symlink__create_symlink() {
  ___target_path="$1"
  ___symlink_path="$2"

  dm__logger__info "Creating the symlink for the given target file.."

  if _dm__symlink__parent_of_target_is_writeable "$___symlink_path"
  then
    posix_adapter__ln --symbolic --path-to-target "$___target_path" --path-to-link "$___symlink_path"
  else
    dm__logger__warning "You don't have sufficient enough privileges to create the symlink.."
    dm__execute_with_privilege posix_adapter__ln --symbolic --path-to-target "$___target_path" --path-to-link "$___symlink_path"
  fi
}

#==============================================================================
# Function that attempts to remove a symlink from a given path.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] symlink_path - Absolute path to the creatable symlink.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Displays the inner workings via the logger interface.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__remove_symlink() {
  ___symlink_path="$1"

  dm__logger__task "${BOLD}Removing symlink..${RESET}"
  dm__logger__log "Path to symlink: ${UNDERLINE}${___symlink_path}${RESET}"

  if [ -L "$___symlink_path" ]
  then
    ___existing_target="$(readlink -f "$___symlink_path")"
    dm__logger__log "${YELLOW}Existing target: ${UNDERLINE}${___existing_target}${RESET}"

    dm__logger__user_input "${YELLOW}Are you sure you want to remove the link? ${BOLD}[y|N]${RESET}"
    if [ "$dm_user_response" = 'y' ]
    then
      _dm__symlink__delete_target "$___symlink_path"
      dm__logger__success "${BOLD}Symlink removed${RESET}"
    else
      dm__logger__success "${BOLD}Aborted by user${RESET}"
    fi
  else
    dm__logger__success "${BOLD}Link was already removed${RESET}"
  fi
}