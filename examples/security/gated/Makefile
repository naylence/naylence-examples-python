.DEFAULT_GOAL := start

# Handle verbose mode via VERBOSE variable or verbose target
VERBOSE ?= false

init:
	@python3 ../scripts/generate_dev_secrets.py --from-subdir

start: init
	docker compose up -d

stop:
	docker compose down --remove-orphans

run:
	@if [ "$(VERBOSE)" = "true" ]; then \
		FAME_SHOW_ENVELOPES=true python client.py; \
	else \
		python client.py; \
	fi

# Verbose mode via explicit target
run-verbose:
	@FAME_SHOW_ENVELOPES=true python client.py

# Alternative verbose target
verbose:
	@$(MAKE) run VERBOSE=true

clean: stop
	@echo "🧹 Cleaning generated files..."
	@cd config && rm -rf .env.client .env.agent .env.oauth2-server .env.sentinel
	@rm -rf ../.secrets
	@rm -rf config/caddy/data
	@echo "✅ Cleaned generated .env files and secrets directory"
