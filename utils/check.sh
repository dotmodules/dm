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
# COLOR VARIABLES
#==============================================================================

if command -v tput >/dev/null && tput init >/dev/null 2>&1
then
  RED=$(tput setaf 1)
  GREEN=$(tput setaf 2)
  RESET=$(tput sgr0)
  BOLD=$(tput bold)
else
  RED=''
  GREEN=''
  RESET=''
  BOLD=''
fi

#==============================================================================
# HEADER
#==============================================================================

echo '========================================================================================================================'
echo ' CODE QUALITY CHECKS'
echo '========================================================================================================================'

#==============================================================================
# CHECK - ISORT
#==============================================================================

output__isort="$(isort --diff --color --profile black dotmodules tests 2>&1)"

if [ -z "$output__isort" ]
then
  status__isort=0
else
  status__isort=1
fi

# The colored isort output has a colorama issue which prevent it to close
# correctly the coloring sequences hence the manual reset on each line ending..
if [ -n "$output__isort" ]
then
  echo "$output__isort" | sed 's/^/ isort  | /' | sed "s/$/$(tput sgr0)/"
fi

#==============================================================================
# CHECK - BLACK
#==============================================================================

output__black="$(black --diff --quiet --color dotmodules tests 2>&1)"

if [ -z "$output__black" ]
then
  status__black=0
else
  status__black=1
fi

if [ -n "$output__black" ]
then
  echo '------------------------------------------------------------------------------------------------------------------------'
  echo "$output__black" | sed 's/^/ black  | /'
fi

#==============================================================================
# CHECK - FLAKE8
#==============================================================================

if output__flake8="$(flake8 dotmodules tests 2>&1)"
then
  status__flake8=0
else
  status__flake8=1
fi

if [ -n "$output__flake8" ]
then
  echo '------------------------------------------------------------------------------------------------------------------------'
  echo "$output__flake8" | sed 's/^/ flake8 | /'
fi

#==============================================================================
# CHECK - BANDIT
#==============================================================================

# Separate bandit run for the module itself with a safety cat.
output__bandit_module="$(bandit --silent --recursive dotmodules 2>&1 | cat)"

if [ -z "$output__bandit_module" ]
then
  status__bandit_module=0
else
  status__bandit_module=1
fi

if [ -n "$output__bandit_module" ]
then
  echo '------------------------------------------------------------------------------------------------------------------------'
  echo "$output__bandit_module" | sed 's/^/ bandit | /'
fi

# Separate bandit run for the test suite with a safety cat.
output__bandit_tests="$(bandit --silent --skip B101 --recursive tests 2>&1 | cat)"

if [ -z "$output__bandit_tests" ]
then
  status__bandit_tests=0
else
  status__bandit_tests=1
fi

if [ -n "$output__bandit_tests" ]
then
  echo '------------------------------------------------------------------------------------------------------------------------'
  echo "$output__bandit_tests" | sed 's/^/ bandit | /'
fi

status__bandit=$((status__bandit_module + status__bandit_tests))

#==============================================================================
# CHECK - MYPY
#==============================================================================

if output__mypy="$(MYPY_FORCE_COLOR=1 mypy dotmodules tests 2>&1)"
then
  status__mypy=0
else
  status__mypy=1
fi

if [ -n "$output__mypy" ]
then
  echo '------------------------------------------------------------------------------------------------------------------------'
  echo "$output__mypy" | sed 's/^/ mypy   | /'
fi


#==============================================================================
# DETAILED STATUS REPORT
#==============================================================================

echo '========================================================================================================================'
echo ' RESULTS'
echo '========================================================================================================================'

if [ "$status__isort" -gt '0' ]
then
  echo " isort  | ${RED}${BOLD}failed${RESET}"
else
  echo " isort  | ${GREEN}${BOLD}passed${RESET}"
fi

if [ "$status__black" -gt '0' ]
then
  echo " black  | ${RED}${BOLD}failed${RESET}"
else
  echo " black  | ${GREEN}${BOLD}passed${RESET}"
fi

if [ "$status__flake8" -gt '0' ]
then
  echo " flake8 | ${RED}${BOLD}failed${RESET}"
else
  echo " flake8 | ${GREEN}${BOLD}passed${RESET}"
fi

if [ "$status__bandit" -gt '0' ]
then
  echo " bandit | ${RED}${BOLD}failed${RESET}"
else
  echo " bandit | ${GREEN}${BOLD}passed${RESET}"
fi

if [ "$status__mypy" -gt '0' ]
then
  echo " mypy   | ${RED}${BOLD}failed${RESET}"
else
  echo " mypy   | ${GREEN}${BOLD}passed${RESET}"
fi

echo '========================================================================================================================'

#==============================================================================
# EXIT STATUS CALCULATION
#==============================================================================

result=$((status__isort + 0))
result=$((status__black + result))
result=$((status__flake8 + result))
result=$((status__bandit + result))
result=$((status__mypy + result))

if [ "$result" -gt '0' ]
then
  exit 1
fi