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
# COMMON ARGUMENTS
#==============================================================================

# Argument 1 - Path prefix to the dotmodules repo root. This is the first
# argument that is passed by this script. This script is only responsible to get
# the this first argument, and then it should source the common script to load
# the common functionality. The common script will handle the common arguments,
# and after it, this script can handle the arguments intended to be parsed by
# this script.
DM_REPO_ROOT="$1"
shift

#==============================================================================
# LOADING THE COMMON TOOLS SCRIPT
#==============================================================================

# shellcheck source=./lib/base.sh
. "${DM_REPO_ROOT}/utils/hooks/lib/base.sh"

#==============================================================================
# HOOK SPECIFIC ARGUMENT PARSING
#==============================================================================

# NOTE: The common script parses 8 arguments. The next argument to be parsed is
# the 9th that is intended to be parsed by the hook scripts.


#==============================================================================
# ENTRY POINT
#==============================================================================

dm__logger__header

___first_item_processed='0'

while [ $# -gt 0 ]
do

  path_to_target="$1"
  path_to_symlink="$2"
  shift
  shift

  if [ "$___first_item_processed" = '0' ]
  then
    ___first_item_processed='1'
  else
    dm__logger__double_separator
  fi

  dm__create_symlink "$path_to_target" "$path_to_symlink"

done


dm__logger__footer