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
# confusing as this script expects to be called from the repository root.
# shellcheck source=../../../utils/posix_adapter_init.sh
. "${DM_REPO_ROOT}/utils/posix_adapter_init.sh"

#==============================================================================
# SUB-MODULE LOADING
#==============================================================================

# shellcheck source=../../../utils/hooks/lib/logger.sh
. "${DM_REPO_ROOT}/utils/hooks/lib/logger.sh"

# shellcheck source=../../../utils/hooks/lib/execution.sh
. "${DM_REPO_ROOT}/utils/hooks/lib/execution.sh"

# shellcheck source=../../../utils/hooks/lib/variables.sh
. "${DM_REPO_ROOT}/utils/hooks/lib/variables.sh"

# shellcheck source=../../../utils/hooks/lib/linking.sh
. "${DM_REPO_ROOT}/utils/hooks/lib/linking.sh"