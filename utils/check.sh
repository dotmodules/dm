#!/bin/sh

#==============================================================================
# SANE ENVIRONMENT
#==============================================================================

# NOTE: exit on error is turned off, as we want to see the failed checkers
# output in the report.
set -u  # prevent unset variable expansion

#==============================================================================
# PATH HANDLING
#==============================================================================

# Changing the path is unnecesary for this script. The invocation path should be
# the repository root.

#==============================================================================
# GLOBAL VARIABLES AND EYECANDY
#==============================================================================

if command -v tput >/dev/null && tput init >/dev/null 2>&1
then
  RED=$(tput setaf 1)
  GREEN=$(tput setaf 2)
  RESET=$(tput sgr0)
  DIM=$(tput dim)
  BOLD=$(tput bold)
else
  RED=''
  GREEN=''
  RESET=''
  DIM=''
  BOLD=''
fi

divider__double__top() {
  echo '════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════'
}

divider__double__header() {
  echo '════════╤═══════════════════════════════════════════════════════════════════════════════════════════════════════════════'
}

divider__double__footer() {
  echo '════════╧═══════════════════════════════════════════════════════════════════════════════════════════════════════════════'
}

divider__inner() {
  echo '────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────'
}

#==============================================================================
# HEADER
#==============================================================================

divider__double__top
echo " ${BOLD}CODE QUALITY CHECKS${RESET}"
divider__double__header

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
  echo "$output__isort" | sed "s/^/ ${DIM}isort${RESET}  │ /" | sed "s/$/$(tput sgr0)/"
else
  echo " ${DIM}isort${RESET}  │ Nothing to report"
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

divider__inner
if [ -n "$output__black" ]
then
  echo "$output__black" | sed "s/^/ ${DIM}black${RESET}  │ /"
else
  echo " ${DIM}black${RESET}  │ Nothing to report"
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

divider__inner
if [ -n "$output__flake8" ]
then
  echo "$output__flake8" | sed "s/^/ ${DIM}flake8${RESET} │ /"
else
  echo " ${DIM}flake8${RESET} │ Nothing to report"
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

divider__inner
if [ -n "$output__bandit_module" ]
then
  echo "$output__bandit_module" | sed "s/^/ ${DIM}bandit${RESET} │ /"
else
  echo " ${DIM}bandit${RESET} │ Nothing to report for module"
fi

# Separate bandit run for the test suite with a safety cat.
output__bandit_tests="$(bandit --silent --skip B101 --recursive tests 2>&1 | cat)"

if [ -z "$output__bandit_tests" ]
then
  status__bandit_tests=0
else
  status__bandit_tests=1
fi

divider__inner
if [ -n "$output__bandit_tests" ]
then
  echo "$output__bandit_tests" | sed "s/^/ ${DIM}bandit${RESET} │ /"
else
  echo " ${DIM}bandit${RESET} │ Nothing to report for test suite"
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

divider__inner
if [ -n "$output__mypy" ]
then
  echo "$output__mypy" | sed "s/^/ ${DIM}mypy${RESET}   │ /"
else
  echo " ${DIM}mypy${RESET}  │ Nothing to report for test suite"
fi


#==============================================================================
# DETAILED STATUS REPORT
#==============================================================================

divider__double__footer
echo " ${BOLD}RESULTS${RESET}"
divider__double__header

if [ "$status__isort" -gt '0' ]
then
  echo " ${DIM}isort${RESET}  │ ${RED}${BOLD}failed${RESET}"
else
  echo " ${DIM}isort${RESET}  │ ${GREEN}${BOLD}passed${RESET}"
fi

if [ "$status__black" -gt '0' ]
then
  echo " ${DIM}black${RESET}  │ ${RED}${BOLD}failed${RESET}"
else
  echo " ${DIM}black${RESET}  │ ${GREEN}${BOLD}passed${RESET}"
fi

if [ "$status__flake8" -gt '0' ]
then
  echo " ${DIM}flake8${RESET} │ ${RED}${BOLD}failed${RESET}"
else
  echo " ${DIM}flake8${RESET} │ ${GREEN}${BOLD}passed${RESET}"
fi

if [ "$status__bandit" -gt '0' ]
then
  echo " ${DIM}bandit${RESET} │ ${RED}${BOLD}failed${RESET}"
else
  echo " ${DIM}bandit${RESET} │ ${GREEN}${BOLD}passed${RESET}"
fi

if [ "$status__mypy" -gt '0' ]
then
  echo " ${DIM}mypy${RESET}   │ ${RED}${BOLD}failed${RESET}"
else
  echo " ${DIM}mypy${RESET}   │ ${GREEN}${BOLD}passed${RESET}"
fi

divider__double__footer

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