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
# the 9th that is intended to be parsed by the hook adapter script.

# Argument 9 - Execution mode of the script.
dm__config__execution_mode="$1"
shift

# Argument 10 - Variable name.
dm__config__variable_name="$1"
shift

# Argument 11 - Variable value that should be checked.
dm__config__variable_value="$1"
shift

# Argument 12 - Target hook script that should be executed.
dm__config__target_hook_script="$1"
shift

#==============================================================================
# ENTRY POINT
#==============================================================================

# Executing the target variable status hook script by passing the execution
# mode, variable name and variable value to be checked. The script output and
# status code will be captured by the called process.
"$dm__config__target_hook_script" \
  "$dm__config__dm_cache_root" \
  "$dm__config__execution_mode" \
  "$dm__config__variable_name" \
  "$dm__config__variable_value"