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