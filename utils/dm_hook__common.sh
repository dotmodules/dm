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

if posix_adapter__tput__is_available
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
  posix_adapter__echo "$(
    python -c 'import sys;print(sys.argv[1]*int(sys.argv[2]))' \
    "$___char" \
    "$___count" \
  )"

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
  line="$1"
  posix_adapter__echo "${dm__config__indent}${line}"
}

#==============================================================================
# VARIABLES
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
  header="HOOK ${BOLD}${dm__config__target_hook_name}${RESET} (${dm__config__target_hook_priority}) - ${dm__config__target_module_name}"

  _dm__utils__indent_line "${DIM}╒$(dm__utils__repeat_character '═' $(("$DM__HEADER_LENGTH" - 1)))${RESET}"
  _dm__utils__indent_line "│ ${header}"
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
  message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}${BOLD}${GREEN} >> ${RESET}${DIM}│${RESET} ${message}"
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
  message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}${BOLD}${CYAN} .. ${RESET}${DIM}│${RESET} ${message}"
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
  message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}${BOLD}${GREEN} ok ${RESET}${DIM}│${RESET} ${message}"
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
  message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}${BOLD}${YELLOW} !! ${RESET}${DIM}│${RESET} ${message}"
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
  message="$1"
  _dm__utils__indent_line "${DIM}│${RESET}${BOLD}${RED} !! ${RESET}${DIM}│${RESET} ${message}"
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
#   dm_response - The response the user typed into the question
# STDOUT:
#   Prints out the prompt.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
dm__logger__user_input() {
  prompt="$1"
  posix_adapter__printf "${dm__config__indent}${DIM}│${RESET}${BOLD}${MAGENTA} ?? ${RESET}${DIM}│${RESET} ${prompt} "
  # shellcheck disable=SC2034
  read -r dm_response
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
  posix_adapter__printf "${dm__config__indent}${DIM}│${RESET}${BOLD}${YELLOW} ?? ${RESET}${DIM}│${RESET} ${YELLOW}Do you want to continue? ${BOLD}[y/N] ${RESET}"
  read -r response
  if [ 'y' = "$response" ]
  then
    sudo \
      --preserve-env \
      --shell \
      --prompt="${dm__config__indent}${DIM}│${RESET}${BOLD}${YELLOW} >> ${RESET}${DIM}│${RESET} ${BOLD}${YELLOW}[sudo] password for ${USER}${RESET}: " \
      "$@" | dm__logger__prefix_lines
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
# provides an interface to get those variables in a global level.

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
  variable_name="$1"
  target_file="${dm__config__dm_cache_variables}/${variable_name}"
  if [ ! -f "$target_file" ]
  then
    dm__logger__error "Invalid variable '${variable_name}'!"
    exit 1
  fi
  posix_adapter__cat "$target_file"
}