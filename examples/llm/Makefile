.DEFAULT_GOAL := build

# Default script if none is provided
SCRIPT ?= echo_agent.py

# Override SCRIPT with first argument if provided
ifneq ($(word 2,$(MAKECMDGOALS)),)
SCRIPT := $(word 2,$(MAKECMDGOALS))
endif

build:
	@docker build -t simple-llm-examples .

stop:
	
run:
	@docker run --rm -it -v .:/work -w /work -e OPENAI_API_KEY=${OPENAI_API_KEY} simple-llm-examples python $(SCRIPT)

run-verbose:
	@docker run --rm -it -v .:/work -w /work -e OPENAI_API_KEY=${OPENAI_API_KEY} simple-llm-examples python $(SCRIPT)

run-ci:
	@docker run --rm -v .:/work -w /work -e OPENAI_API_KEY=${OPENAI_API_KEY} simple-llm-examples python $(SCRIPT)

clean: stop
	@echo "🧹 Nothing to clean"

# Catch-all rule to prevent make from trying to execute script names as targets
%:
	@:
