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

# Argument 9 - Target hook script that should be executed.
dm__config__target_hook_script="$1"
shift

#==============================================================================
# ENTRY POINT
#==============================================================================

dm__logger__header

# As we are executing the hook script dinamically, we cannot know the exact path
# of the script before it this script is executed, hence the disabled shellcheck
# warning about it.
# shellcheck disable=SC1090
. "$dm__config__target_hook_script"

dm__logger__footer