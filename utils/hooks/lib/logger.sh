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

if [ -z ${dm__config__wrap_limit+x} ]
then
  echo "Using default value for variable: dm__config__wrap_limit"
  dm__config__wrap_limit=90
fi

if [ -z ${dm__config__indent+x} ]
then
  echo "Using default value for variable: dm__config__indent"
  dm__config__indent="  "
fi

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