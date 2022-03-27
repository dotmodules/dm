#!/bin/sh

#==============================================================================
# SANE ENVIRONMENT
#==============================================================================

set -e  # exit on error
set -u  # prevent unset variable expansion

#==============================================================================
# PATH HANDLING
#==============================================================================

# It is known that on MacOS readlink does not support the -f flag by default.
# https://stackoverflow.com/a/4031502/1565331
if DM_REPO_ROOT="$(dirname "$(readlink -f "$0" 2>/dev/null)")"
then
  :
else
  # If the path cannot be determined with readlink, we have to check if this
  # script is executed through a symlink or not.
  if [ -L "$0" ]
  then
    # If the current script is executed through a symlink, we are aout of luck,
    # because without readlink, there is no universal solution for this problem
    # that uses the default shell toolset.
    echo 'Symlinked script won'\''t work on this machine..'
    echo 'Make sure you install a readlink version that supports the -f flag.'
  else
    # If the current script is not executed through a symlink, we can determine
    # the path with dirname.
    DM_REPO_ROOT="$(dirname "$0")"
  fi
fi

#==============================================================================
# POSIX_ADAPTER INTEGRATION
#==============================================================================

#==============================================================================
# The first module we are loading is the posix-adapter project that would
# provide the necessary platform independent interface for the command line
# tools. We are only loading the posix-adapter system when it hasn't been loaded
# by other code (the tested system for example).
#==============================================================================

if [ -z ${POSIX_ADAPTER__READY+x} ]
then
  # If posix_adapter has not sourced yet, we have to source it from this
  # repository.  Implementing the posix-adapter inporting system variables.
  ___posix_adapter_path_prefix="${DM_REPO_ROOT}/dependencies/posix-adapter"
  POSIX_ADAPTER__CONFIG__MANDATORY__SUBMODULE_PATH_PREFIX="$___posix_adapter_path_prefix"
  if [ -d "$POSIX_ADAPTER__CONFIG__MANDATORY__SUBMODULE_PATH_PREFIX" ]
  then
    # shellcheck source=./dependencies/posix-adapter/posix_adapter.sh
    . "${POSIX_ADAPTER__CONFIG__MANDATORY__SUBMODULE_PATH_PREFIX}/posix_adapter.sh"
  else
      echo 'Initialization failed!'
      echo 'posix_adapter needs to be initialized but its git submodule is missing!'
      echo 'You need to init the dotmodules repository: make init'
  fi
fi

#==============================================================================
# GLOBAL VARIABLES
#==============================================================================

VERSION=$(posix_adapter__cat "${DM_REPO_ROOT}/VERSION")
DEFAULT_MODULES_DIR='modules'
MAKEFILE_TEMPLATE_PATH='templates/Makefile.template'
MAKEFILE_NAME='Makefile'

if posix_adapter__tput__is_available
then
  RED=$(posix_adapter__tput setaf 1)
  RED_BG=$(posix_adapter__tput setab 1)
  GREEN=$(posix_adapter__tput setaf 2)
  YELLOW=$(posix_adapter__tput setaf 3)
  BLUE=$(posix_adapter__tput setaf 4)
  MAGENTA=$(posix_adapter__tput setaf 5)
  CYAN=$(posix_adapter__tput setaf 6)
  RESET=$(posix_adapter__tput sgr0)
  BOLD=$(posix_adapter__tput bold)
else
  RED=''
  RED_BG=''
  GREEN=''
  YELLOW=''
  BLUE=''
  MAGENTA=''
  CYAN=''
  RESET=''
  BOLD=''
fi

#==============================================================================
# FUNCTIONS
#==============================================================================

#==============================================================================
# Function that prints out the documentation to its standard output.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   None
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Documentation.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
print_documentation() {
posix_adapter__cat <<EOM
- DOTMODULES ${VERSION} ------------------------------------------------------------
   _           _        _ _       _
  (_)         | |      | | |     | |
   _ _ __  ___| |_ __ _| | |  ___| |__
  | | '_ \\/ __| __/ _\` | | | / __| '_ \\
  | | | | \\__ \\ || (_| | | |_\\__ \\ | | |
  |_|_| |_|___/\\__\\__,_|_|_(_)___/_| |_|


  ${BOLD}DOCUMENTATION${RESET}

    Installer script for the ${BOLD}dotmodules${RESET} configuration management system. It
    assumes that you added ${BOLD}dotmodules${RESET} to your dotfiles repo as a submodule,
    and you are invoking this script from your dotfiles repository root.

    The script will calculate the necessary relative paths needed for proper
    operation and with that information it will generate a Makefile to your
    dotfile repo's root.

    This Makefile will be the main entry point to interact with ${BOLD}dotmodules${RESET}.


  ${BOLD}PARAMETERS${RESET}

    ${BOLD}-h|--help${RESET}

      Prints out this help message.

    ${BOLD}-m|--modules <modules_directory>${RESET}

      By default ${BOLD}dotmodules${RESET} will look for the '${DEFAULT_MODULES_DIR}' directory in your
      dotfiles repo, but you can pass a custom directory name with this flag.

EOM
}

#==============================================================================
# Function that calculates the relative path fot the given target path from the
# dm repository root directory. It is used to populate the paths in the
# generated Makefile.
#------------------------------------------------------------------------------
# Globals:
#   None
# Arguments:
#   [1] origin_path - Path the calculation should be based from.
#   [2] target_path - Target path for which the relative path should be
#       calculate to from the dm repository root.
# STDIN:
#   None
#------------------------------------------------------------------------------
# Output variables:
#   None
# STDOUT:
#   Relative path to the target path.
# STDERR:
#   None
# Status:
#   0 - Other status is not expected.
#==============================================================================
calculate_relative_path_for() {
  origin_path="$1"
  target_path="$2"
  posix_adapter__realpath --relative-to "$origin_path" "$target_path"
}

#==============================================================================
# PARAMETER PARSING
#==============================================================================

MODULES_DIR="${DEFAULT_MODULES_DIR}"

while [ $# -gt 0 ]
do
  key="$1"
  case $key in
    -h|--help)
      print_documentation
      exit 0
      ;;
    -m|--modules)
      MODULES_DIR="$2"
      shift
      shift
      ;;
    *)
      ;;
  esac
done

#==============================================================================
# ENTRY POINT
#==============================================================================

posix_adapter__echo ''
posix_adapter__echo "  ${BOLD}DOTMODULES INSTALLER SCRIPT${RESET}"
posix_adapter__echo ''

relative_modules_path="$(calculate_relative_path_for "${DM_REPO_ROOT}" "$(pwd)/${MODULES_DIR}")"
relative_dm_repo_root_path="$(calculate_relative_path_for "$(pwd)" "${DM_REPO_ROOT}")"

posix_adapter__echo "    Current working directory: ${BLUE}$(pwd)${RESET}"
posix_adapter__echo "    Dotmodules repository root: ${BLUE}${DM_REPO_ROOT}${RESET}"
posix_adapter__echo "    Modules directory path: ${BLUE}$(pwd)/${MODULES_DIR}${RESET}"
posix_adapter__echo "    Calculated relative modules directory path: ${GREEN}${relative_modules_path}${RESET}"

# Substitute calculated variables to the Makefile template and place it to the
# invocation's directory.
posix_adapter__sed \
  --expression "s#__RELATIVE_DM_ROOT_PATH__#${relative_dm_repo_root_path}#" \
  "${DM_REPO_ROOT}/${MAKEFILE_TEMPLATE_PATH}" > "${MAKEFILE_NAME}"
posix_adapter__sed \
  --in-place '' \
  --expression "s#__RELATIVE_MODULES_PATH__#${relative_modules_path}#" \
  "${MAKEFILE_NAME}"

posix_adapter__echo ''
posix_adapter__echo "    ${BOLD}Makefile template generated.${RESET}"
