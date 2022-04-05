#!/bin/sh

# This script should be sourced into every script that wants to use the posix
# adapter layer. It expects that the invocation script has set the current path
# to the repository root.

if [ -z ${DM_REPO_ROOT+x} ]
then
  # If the DM_REPO_ROOT variable is not set, it is presumed that this script was
  # sourced from the repository root.
  DM_REPO_ROOT="$(pwd)"
fi

if [ -z ${POSIX_ADAPTER__READY+x} ]
then
  # If posix_adapter has not sourced yet, we have to source it from this
  # repository. Implementing the posix-adapter inporting system variables.
  posix_adapter_path_prefix="${DM_REPO_ROOT}/dependencies/posix-adapter"
  POSIX_ADAPTER__CONFIG__MANDATORY__SUBMODULE_PATH_PREFIX="$posix_adapter_path_prefix"
  if [ -d "$POSIX_ADAPTER__CONFIG__MANDATORY__SUBMODULE_PATH_PREFIX" ]
  then
    # shellcheck source=../dependencies/posix-adapter/posix_adapter.sh
    . "${POSIX_ADAPTER__CONFIG__MANDATORY__SUBMODULE_PATH_PREFIX}/posix_adapter.sh"
  else
      echo 'Initialization failed!'
      echo 'posix_adapter needs to be initialized but its git submodule is missing!'
      echo 'You need to init the dotmodules repository: make init'
      exit 1
  fi
fi