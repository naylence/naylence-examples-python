.DEFAULT_GOAL := start

# Default script if none is provided
SCRIPT ?= echo_agent.py

# Override SCRIPT with first argument if provided
ifneq ($(word 2,$(MAKECMDGOALS)),)
SCRIPT := $(word 2,$(MAKECMDGOALS))
endif

start:
	

stop:
	

run:
	@docker run --rm -v .:/work -w /work naylence/agent-sdk-python:0.2.1 python $(SCRIPT)

run-verbose:
	@docker run --rm -v .:/work -w /work naylence/agent-sdk-python:0.2.1 python $(SCRIPT)

clean: stop
	@echo "🧹 Nothing to clean"

# Catch-all rule to prevent make from trying to execute script names as targets
%:
	@:
