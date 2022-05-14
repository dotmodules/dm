#!/bin/sh

#==============================================================================
# SANE ENVIRONMENT
#==============================================================================

set -e  # exit on error
set -u  # prevent unset variable expansion

#==============================================================================
# PATH HANDLING
#==============================================================================

# Changing the path is unnecesary for this script. The working directory will be
# the given module's configuration root. If we want to reach the dotmodules
# repository root, there is a handy relative prefix that is passed to this
# script as the first argument.

#==============================================================================
# COMMON PARAMETERS
#==============================================================================

# Argument 1 - Has been already parsed by the caller of this script.

# Argument 2 - Target hook name.
dm__config__target_hook_name="$1"
shift

# Argument 3 - Target hook priority.
dm__config__target_hook_priority="$1"
shift

# Argument 4 - Target module name the hook is executed for.
dm__config__target_module_name="$1"
shift

# Argument 5 - Path to the dotmodules cache root directory.
dm__config__dm_cache_root="$1"
shift

# Argument 6 - Path to the dotmodules variables cache directory.
dm__config__dm_cache_variables="$1"
shift

# Argument 7 - Global indent string each line should be prefixed with.
dm__config__indent="$1"
shift

# Argument 8 - Global wrap limit that should be respected.
dm__config__wrap_limit="$1"
shift

#==============================================================================
# POSIX_ADAPTER INTEGRATION
#==============================================================================

# The shellcheck source path have to be relative to the file itself. It can be
# confusing as this script expectes to be called from the repository root.
# shellcheck source=../utils/posix_adapter_init.sh
. "${DM_REPO_ROOT}/utils/posix_adapter_init.sh"

#==============================================================================
# COLOR HANDLING
#==============================================================================

if posix_adapter__tput --is-available
then
  RED="$(posix_adapter__tput setaf 1)"
  GREEN="$(posix_adapter__tput setaf 2)"
  YELLOW="$(posix_adapter__tput setaf 3)"
  BLUE="$(posix_adapter__tput setaf 4)"
  MAGENTA="$(posix_adapter__tput setaf 5)"
  CYAN="$(posix_adapter__tput setaf 6)"
  RESET="$(posix_adapter__tput sgr0)"
  BOLD="$(posix_adapter__tput bold)"
  DIM="$(posix_adapter__tput dim)"
  HIGHLIGHT="$(posix_adapter__tput smso)"
  UNDERLINE="$(posix_adapter__tput smul)"
else
  RED=''
  GREEN=''
  YELLOW=''
  BLUE=''
  MAGENTA=''
  CYAN=''
  RESET=''
  BOLD=''
  DIM=''
fi

#==============================================================================
# UTILITY HELPER FUNCTIONS
#==============================================================================

# Calculating the header length based on the indent and global text wrap limit.
DM__HEADER_LENGTH="$(
  python -c 'import sys;print(int(sys.argv[1])-len(sys.argv[2]))' \
  "$dm__config__wrap_limit" \
  "$dm__config__indent"\
)"

#==============================================================================
# Triggers the [setup] hook.
#------------------------------------------------------------------------------
# Globals:
#   POSIX_TEST__HOOKS__CONFIG__FUNCTION_NAME__SETUP
#   POSIX_TEST__HOOKS__RUNTIME__FLAG__SETUP
# Arguments:
#   None
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Outputs the given hook's output.
# STDERR:
#   Outputs the given hook's error output.
# Status:
#   Returns the given hook's status.
#==============================================================================
dm__utils__repeat_character() {
  ___char="$1"
  ___count="$2"
  python -c 'import sys;print(sys.argv[1]*int(sys.argv[2]))' \
    "$___char" \
    "$___count" \

}

#==============================================================================
# Triggers the [setup] hook.
#------------------------------------------------------------------------------
# Globals:
#   POSIX_TEST__HOOKS__CONFIG__FUNCTION_NAME__SETUP
#   POSIX_TEST__HOOKS__RUNTIME__FLAG__SETUP
# Arguments:
#   None
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Outputs the given hook's output.
# STDERR:
#   Outputs the given hook's error output.
# Status:
#   Returns the given hook's status.
#==============================================================================
_dm__utils__indent_line() {
  ___line="$1"
  echo "${dm__config__indent}${___line}"
}

#==============================================================================
# PRETTY LOGGING
#==============================================================================

#==============================================================================
# Prints out the header.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   RESET
#   DM__HEADER_LENGTH
# Arguments:
#   None
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out the heder with the given text.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__header() {
  ___header="HOOK ${BOLD}${dm__config__target_hook_name}${RESET} (${dm__config__target_hook_priority}) - ${dm__config__target_module_name}"

  _dm__utils__indent_line "${DIM}╒$(dm__utils__repeat_character '═' $(("$DM__HEADER_LENGTH" - 1)))${RESET}"
  _dm__utils__indent_line "${DIM}│${RESET} ${___header}"
  _dm__utils__indent_line "${DIM}╞════╤$(dm__utils__repeat_character '═' $(("$DM__HEADER_LENGTH" - 6)))${RESET}"
}

#==============================================================================
# Lines directed to the standard input of this function will be printed in a
# pretty way.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   RESET
# Arguments:
#   None
# STDIN:
#   Lines that will be pretty printed.
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out the piped lines in a pretty way.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__prefix_lines() {
  posix_adapter__cat - | \
    posix_adapter__sed \
    --expression "s/^/${dm__config__indent}${DIM}│    │${RESET} /"
}

#==============================================================================
# Prints out a task message.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   GREEN
#   RESET
# Arguments:
#   [1] message - The task message that should be printed.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out the task message.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__task() {
  ___message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}${BOLD}${GREEN} >> ${RESET}${DIM}│${RESET} ${___message}"
}

#==============================================================================
# Prints out a log message without any eyecandy.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   CYAN
#   RESET
# Arguments:
#   [1] message - The log message that should be printed.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out the info message.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__log() {
  ___message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}    ${DIM}│${RESET} ${___message}"
}

#==============================================================================
# Prints out a info message.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   CYAN
#   RESET
# Arguments:
#   [1] message - The info message that should be printed.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out the info message.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__info() {
  ___message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}${BOLD}${CYAN} .. ${RESET}${DIM}│${RESET} ${___message}"
}

#==============================================================================
# Prints out a success message.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   GREEN
#   RESET
# Arguments:
#   [1] message - The success message that should be printed.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out the success message.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__success() {
  ___message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}${BOLD}${GREEN} ok ${RESET}${DIM}│${RESET} ${___message}"
}

#==============================================================================
# Prints out a warning message.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   YELLOW
#   RESET
# Arguments:
#   [1] message - The warning message that should be printed.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out the warning message.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__warning() {
  ___message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}${BOLD}${YELLOW} !! ${RESET}${DIM}│${RESET} ${___message}"
}

#==============================================================================
# Prints out an error message.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   RED
#   RESET
# Arguments:
#   [1] message - The error message that should be printed.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out the error message.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__error() {
  ___message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}${BOLD}${RED} !! ${RESET}${DIM}│${RESET} ${___message}"
}

#==============================================================================
# Prints out the given prompt and collects the answer from the user into an
# output variable.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   MAGENTA
#   RESET
# Arguments:
#   [1] prompt - The prompt the user should response to.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   dm_user_response - The response the user typed into the question
# STDOUT:
#   Prints out the prompt.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__user_input() {
  ___prompt="$1"
  printf '%s' "${dm__config__indent}${DIM}│${RESET}${BOLD}${MAGENTA} ?? ${RESET}${DIM}│${RESET} ${___prompt} "
  # shellcheck disable=SC2034
  read -r dm_user_response
}

#==============================================================================
# Prints out a separator.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   RESET
#   DM__HEADER_LENGTH
# Arguments:
#   None
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out a separator.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__separator() {
  _dm__utils__indent_line "${DIM}├────┼$(dm__utils__repeat_character '─' $(("$DM__HEADER_LENGTH" - 6)))${RESET}"
}

#==============================================================================
# Prints out a double separator.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   RESET
#   DM__HEADER_LENGTH
# Arguments:
#   None
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out a separator.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__double_separator() {
  _dm__utils__indent_line "${DIM}╞════╪$(dm__utils__repeat_character '═' $(("$DM__HEADER_LENGTH" - 6)))${RESET}"
}

#==============================================================================
# Prints out the footer.
#------------------------------------------------------------------------------
# Globals:
#   DIM
#   RESET
#   DM__HEADER_LENGTH
# Arguments:
#   None
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out the footer.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__footer() {
  _dm__utils__indent_line "${DIM}╘════╧$(dm__utils__repeat_character '═' $(("$DM__HEADER_LENGTH" - 6)))${RESET}"
}

#==============================================================================
# COMMAND EXECUTION
#==============================================================================

#==============================================================================
# Executes a command and displays the output in a dm compatible way.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [..] command - Command with optional parameters to be executed.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Displays the result of the execution in a nicely formatted way.
# STDERR:
#   None
# Status:
#   Proxies the status of the execution.
#==============================================================================
dm__execute() {
    "$@" | dm__logger__prefix_lines
}

#==============================================================================
# Executes a command with elevated privileges. Before it does so it asks for a
# confirmation. If the execution gets confirmed, it asks for the sudo password
# and execute the passed command the disables the sudo timestamp. In this way it
# will ask for the password at every time it executes a command.
#------------------------------------------------------------------------------
# Globals:
#   YELLOW
#   BOLD
#   HIGHLIGHT
#   RESET
# Arguments:
#   [..] command - Command with optional parameters to be executed with elevated
#                  privileges.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Displays the whole flow and prints the captured execution logs too.
# STDERR:
#   None
# Status:
#   0 - Request confirmed, command executed.
#   1 - Request discarded by user.
#==============================================================================
dm__execute_with_privilege() {
  dm__logger__separator
  dm__logger__warning "${YELLOW}About to run command with elevated privilege:${RESET}"
  dm__logger__warning "${BOLD}${YELLOW}${HIGHLIGHT}${*}${RESET}"
  printf '%s' "${dm__config__indent}${DIM}│${RESET}${BOLD}${YELLOW} ?? ${RESET}${DIM}│${RESET} ${YELLOW}Do you want to continue? ${BOLD}[y/N] ${RESET}"
  read -r ___response
  if [ 'y' = "$___response" ]
  then
    # Removing existing timestamp if there is any.
    sudo --reset-timestamp
    sudo \
      --preserve-env \
      --prompt="${dm__config__indent}${DIM}│${RESET}${BOLD}${YELLOW} >> ${RESET}${DIM}│${RESET} ${BOLD}${YELLOW}[sudo] password for ${USER}${RESET}: " \
      "$@" 2>&1 | dm__logger__prefix_lines
    sudo --reset-timestamp
  else
    dm__logger__warning "${YELLOW}Aborted by user..${RESET}"
    dm__logger__footer
    exit 1
  fi
  dm__logger__separator
}

#==============================================================================
# VARIABLES
#==============================================================================

# The dotmodules system collects the registered variables from every modules and
# provides an interface to get those variables in an aggregated way written into
# cache files.

#==============================================================================
# Function that return the given variable's registered values.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] variable_name - Name of the variable you want to get the values for.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Prints out the registered values for the variable one value per line.
# STDERR:
#   None
# Status:
#   0 - Variable exists and values are printed.
#   1 - Variable cannot be found.
#==============================================================================
dm__get_variable() {
  ___variable_name="$1"
  target_file="${dm__config__dm_cache_variables}/${___variable_name}"
  if [ ! -f "$target_file" ]
  then
    dm__logger__error "Invalid variable '${___variable_name}'!"
    exit 1
  fi
  posix_adapter__cat "$target_file"
}

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
#   [1] path_to_file - Absolute path to the linkable file.
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
  ___path_to_file="$1"
  ___path_to_symlink="$2"

  dm__logger__task "${BOLD}Linking symlink..${RESET}"
  dm__logger__log "Path to file:    ${UNDERLINE}${___path_to_file}${RESET}"
  dm__logger__log "Path to symlink: ${UNDERLINE}${___path_to_symlink}${RESET}"

  if [ -L "$___path_to_symlink" ]
  then
    ___existing_target="$(posix_adapter__readlink --canonicalize "$___path_to_symlink")"
    if [ "$___path_to_file" = "$___existing_target" ]
    then
      dm__logger__success "${BOLD}Required symlink already exists. Nothing to do.${RESET}"
      return 0
    fi
    dm__logger__separator
    dm__logger__warning "${BOLD}${YELLOW}Symlink already exists with a different target!${RESET}"
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
          _dm__symlink__delete_symlink "$___path_to_symlink"
          dm__logger__log "${YELLOW}Existing symlink removed${RESET}"
          dm__logger__separator
          break
          ;;
        b)
          # Backing up the existing symlink.
          _dm__symlink__backup_symlink "$___path_to_symlink"
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

  _dm__symlink__create_symlink "$___path_to_file" "$___path_to_symlink"

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
  ___path_to_symlink="$1"
  ___symlink_dir="$(posix_adapter__dirname "$___path_to_symlink")"

  dm__logger__info "Creating the parent directory of the symlink.."

  if [ -d "$___symlink_dir" ]
  then
    dm__logger__log "Directory already exists"
    return 0
  fi
  if posix_adapter__mkdir --parent "$___symlink_dir"
  then
    :
  else
    dm__logger__warning "You don't have sufficient enough privileges to prepare the symlink's directory.."
    dm__execute_with_privilege posix_adapter__mkdir --parent "$___symlink_dir"
  fi

  dm__logger__log "Symlink parent directory created"
}

#==============================================================================
# Creates a backup for the given symlink by moving it to another file. It will
# ask for elevated privileges if needed.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] path_to_symlink - Absolute path to the backupable symlink.
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
_dm__symlink__backup_symlink() {
  ___path_to_symlink="$1"
  ___path_to_backup_symlink="${___path_to_symlink}.backup_$(date +"%s")"

  dm__logger__info "${YELLOW}Backing up the existing symlink..${RESET}"

  if [ -w "$___path_to_backup_symlink" ]
  then
    mv "$___path_to_symlink" "$___path_to_backup_symlink"
  else
    dm__logger__warning "${YELLOW}You don't have sufficient enough privileges to backup the existing symlink..${RESET}"
    dm__execute_with_privilege mv "$___path_to_symlink" "$___path_to_backup_symlink"
  fi

  dm__logger__log " ${YELLOW}Existing link backed up: ${UNDERLINE}${___path_to_backup_symlink}${RESET}"
}

#==============================================================================
# Removes the existing symlink. It will ask for elevated privileges if needed.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] path_to_symlink - Absolute path to the deletable symlink.
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
_dm__symlink__delete_symlink() {
  ___path_to_symlink="$1"
  ___symlink_dir="$(posix_adapter__dirname "$___path_to_symlink")"

  dm__logger__info "${YELLOW}Removing the existing symlink..${RESET}"

  if [ -w "$___symlink_dir" ]
  then
    posix_adapter__rm --force "$___path_to_symlink"
  else
    dm__logger__warning "${YELLOW}You don't have sufficient enough privileges to delete the existing symlink..${RESET}"
    dm__execute_with_privilege posix_adapter__rm --force "$___path_to_symlink"
  fi
}

#==============================================================================
# Creates the symlink for the given file path. It will ask for elevated
# privileges if needed.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] path_to_file - Absolute path to the linkable file.
#   [2] path_to_symlink - Absolute path to the creatable symlink.
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
  ___path_to_file="$1"
  ___path_to_symlink="$2"
  ___symlink_dir="$(posix_adapter__dirname "$___path_to_symlink")"

  dm__logger__info "Creating the symlink for the given target file.."

  if [ -w "$___symlink_dir" ]
  then
    posix_adapter__ln --symbolic --path-to-file "$___path_to_file" --path-to-link "$___path_to_symlink"
  else
    dm__logger__warning "You don't have sufficient enough privileges to create the symlink.."
    dm__execute_with_privilege posix_adapter__ln --symbolic --path-to-file "$___path_to_file" --path-to-link "$___path_to_symlink"
  fi
}

#==============================================================================
# Function that attempts to remove a symlink from a given path.
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
#   Displays the inner workings via the logger interface.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__remove_symlink() {
  ___path_to_symlink="$1"

  dm__logger__task "${BOLD}Removing symlink..${RESET}"
  dm__logger__log "Path to symlink: ${UNDERLINE}${___path_to_symlink}${RESET}"

  if [ -L "$___path_to_symlink" ]
  then
    ___existing_target="$(readlink -f "$___path_to_symlink")"
    dm__logger__log "${YELLOW}Existing target: ${UNDERLINE}${___existing_target}${RESET}"

    dm__logger__user_input "${YELLOW}Are you sure you want to remove the link? ${BOLD}[y|N]${RESET}"
    if [ "$dm_user_response" = 'y' ]
    then
      _dm__symlink__delete_symlink "$___path_to_symlink"
      dm__logger__success "${BOLD}Symlink removed${RESET}"
    else
      dm__logger__success "${BOLD}Aborted by user${RESET}"
    fi
  else
    dm__logger__success "${BOLD}Link was already removed${RESET}"
  fi
}