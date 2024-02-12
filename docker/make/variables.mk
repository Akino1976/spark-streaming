# ANSI escape codes for color formatting
DEBUG := \033[0;36m # cyan (for debug messages)
INFO := \033[0;32m # green (for informational messages)
WARNING := \033[0;33m # yellow (for warning messages)
ERROR := \033[0;31m # red (for error messages)
CRITICAL := \033[1;31m # bold red (for critical errors)
COLOUR_OFF := \033[0m # reset text color

TERRAFORM := ./infrastructure
COMPOSE_DEFAULT_FLAGS := -f docker-compose.yaml
COMPOSE_TEST_FLAGS := $(COMPOSE_DEFAULT_FLAGS) -f docker-compose-test.yaml -f docker-compose-framework.yaml
