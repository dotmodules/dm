# =============================================================================
#  MAKE SETTINGS

.DEFAULT_GOAL := help
SHELL := /bin/sh
NAME := DOTMODULES

# =============================================================================
#  HELPER VARIABLES

BOLD    := $(shell tput bold 2>/dev/null)
RED     := $(shell tput setaf 1 2>/dev/null)
GREEN   := $(shell tput setaf 2 2>/dev/null)
YELLOW  := $(shell tput setaf 3 2>/dev/null)
BLUE    := $(shell tput setaf 4 2>/dev/null)
MAGENTA := $(shell tput setaf 5 2>/dev/null)
CYAN    := $(shell tput setaf 6 2>/dev/null)
RESET   := $(shell tput sgr0 2>/dev/null)

# =============================================================================
#  HELP COMMAND

.PHONY: help
help:
	@echo ""
	@echo "   $(BOLD)$(NAME)$(RESET) make interface"
	@echo "$(BOLD)$(BLUE)=================================================================================$(RESET)"
	@echo ""
	@echo "   $(BOLD)$(BLUE)help$(RESET)                     Prints out this help message."
	@echo "   $(BOLD)$(BLUE)docs$(RESET)                     Generates the documentation for the project."
	@echo "   $(BOLD)$(MAGENTA)init$(RESET)                     Initializes the dev environment (python3 required)."
	@echo "   $(BOLD)$(CYAN)test$(RESET)                     Runs every test suite."
	@echo "   $(BOLD)$(GREEN)test_python$(RESET)              Runs the full python test suite."
	@echo "   $(BOLD)$(GREEN)test_python_unit$(RESET)         Runs the unit tests related python test suite."
	@echo "   $(BOLD)$(GREEN)test_python_integration$(RESET)  Runs the integration tests related python test suite."
	@echo "   $(BOLD)$(CYAN)test_shell$(RESET)               Runs the shell test suite."
	@echo "   $(BOLD)$(YELLOW)check$(RESET)                    Checks for formatting issues."
	@echo "   $(BOLD)$(YELLOW)fix$(RESET)                      Auto formats the code base."
	@echo "   $(BOLD)$(RED)clean$(RESET)                    Cleans up all build/running artifacts."
	@echo ""

# =============================================================================
#  REPOSITORY INIT

.PHONY: init
init:
	@git submodule update --init --recursive

# =============================================================================
#  DEV ENVIRONMENT COMMANDS

.PHONY: dev_init
dev_init: virtualenv_activated
	@pip install --requirement requirements-dev.txt 2>&1 | sed 's/^/pip    | /'
	@safety check --file requirements-dev.txt 2>&1 | sed 's/^/safety | /'

.PHONY: check
check: virtualenv_activated
	@./utils/check.sh

.PHONY: fix
fix: virtualenv_activated
	@isort --color --profile black dotmodules tests dm.py 2>&1 | sed 's/^/isort | /'
	@black dotmodules tests dm.py 2>&1 | sed 's/^/black | /'

.PHONY: test_python_unit
test_python_unit: virtualenv_activated
	@python -m pytest -vv -c pytest.ini \
		-m 'not integration' \
		--cov=dotmodules/ \
		--cov=tests/python/unit_tests \
		tests/python/unit_tests \
		dotmodules

.PHONY: test_python_integration
test_python_integration: virtualenv_activated
	@python -m pytest -vv -c pytest.ini \
		-m integration \
		--cov=dotmodules/ \
		--cov=tests/python/integration_tests \
		tests/python/integration_tests \
		dotmodules

.PHONY: test_python
test_python: virtualenv_activated
	@python -m pytest -vv -c pytest.ini \
		--cov=dotmodules/ \
		--cov=tests/python \
		tests/python \
		dotmodules

.PHONY: test_shell
test_shell:
	@./tests/shell/run.sh

.PHONY: test
test: test_python test_shell
	@echo 'Running the test suites..'

.PHONY: virtualenv_activated
virtualenv_activated:
	@if [ -z "${VIRTUAL_ENV}" ]; then \
		echo "$(BOLD)$(RED)No python virtual env present.$(RESET)"; \
		echo "$(BOLD)$(RED)Create/activate one before you can use the make interface!$(RESET)"; \
		exit 1; \
	fi

.PHONY: clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} \;
	rm -rf docs/_build