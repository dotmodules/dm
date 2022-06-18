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
