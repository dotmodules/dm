#!/bin/sh

#==============================================================================
# SANE ENVIRONMENT
#==============================================================================

set -e  # exit on error
set -u  # prevent unset variable expansion

#==============================================================================
# PATH HANDLING
#==============================================================================

# Changing the path is unnecesary for this script. The invocation path should be
# the repository root.

#==============================================================================
# POSIX_ADAPTER INTEGRATION
#==============================================================================

# The shellcheck source path have to be relative to the file itself. It can be
# confusing as this script expectes to be called from the repository root.
# shellcheck source=../utils/posix_adapter_init.sh
. "utils/posix_adapter_init.sh"

#==============================================================================
# COLOR AND FORMATTING
#==============================================================================

if posix_adapter__tput --is-available
then
  posix_adapter__tput "$@"
else
  echo ''
fi