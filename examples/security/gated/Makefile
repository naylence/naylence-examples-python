# Docker image for Naylence Agent SDK
DOCKER_IMAGE := naylence/agent-sdk-python:0.3.14

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
		docker run --rm \
		-v "$(shell pwd):/work:ro" \
		-v "$(shell basename "$(shell pwd)")_caddy-data:/caddy-data:ro" \
		-w /work \
		--network "$(shell basename "$(shell pwd)")_naylence-net" \
		--env-file config/.env.client \
		-e FAME_SHOW_ENVELOPES=true \
		$(DOCKER_IMAGE) \
		python client.py; \
	else \
		docker run --rm \
		-v "$(shell pwd):/work:ro" \
		-v "$(shell basename "$(shell pwd)")_caddy-data:/caddy-data:ro" \
		-w /work \
		--network "$(shell basename "$(shell pwd)")_naylence-net" \
		--env-file config/.env.client \
		$(DOCKER_IMAGE) \
		python client.py; \
	fi

# Verbose mode via explicit target
run-verbose:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-v "$(shell basename "$(shell pwd)")_caddy-data:/caddy-data:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file config/.env.client \
	-e FAME_SHOW_ENVELOPES=true \
	$(DOCKER_IMAGE) \
	python client.py

# Alternative verbose target
verbose:
	@$(MAKE) run VERBOSE=true

clean: stop
	@echo "🧹 Cleaning generated files..."
	@cd config && rm -rf .env.client .env.agent .env.oauth2-server .env.sentinel
	@echo "🧹 Cleaning secrets directory with Docker..."
	@docker run --rm \
		-v "$(shell pwd)/../..:/work" \
		-w /work \
		$(DOCKER_IMAGE) \
		rm -rf ./security/.secrets 2>/dev/null || true
	@echo "🧹 Removing Caddy named volume..."
	@docker volume rm "$(shell basename "$(shell pwd)")_caddy-data" 2>/dev/null || true
	@echo "✅ Cleaned generated .env files, secrets directory, and Caddy volume"
