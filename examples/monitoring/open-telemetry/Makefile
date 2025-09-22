DOCKER_IMAGE := naylence/open-telemetry-base:0.3.1
COMPOSE_PROJECT_NAME := open-telemetry

.DEFAULT_GOAL := start

init:
	docker compose build
	@docker run --rm \
	-v "$(shell pwd)/../..:/work" \
	-w /work/$(shell basename "$(shell dirname "$(shell pwd)")")/$(shell basename "$(shell pwd)") \
	$(DOCKER_IMAGE) \
	python ../../security/scripts/generate_dev_secrets.py --from-subdir

build:
	docker compose build

build-no-cache:
	docker compose build --no-cache

start: init
	docker compose -p $(COMPOSE_PROJECT_NAME) up -d

stop:
	docker compose -p $(COMPOSE_PROJECT_NAME) down --remove-orphans

run:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-v "$(shell pwd)/config/client-config.yml:/etc/fame/fame-config.yml:ro" \
	-v "$(shell basename "$(shell pwd)")_caddy-data:/caddy-data:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file config/.env.client \
	$(DOCKER_IMAGE) \
	python client.py

run-verbose:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-v "$(shell pwd)/config/client-config.yml:/etc/fame/fame-config.yml:ro" \
	-v "$(shell basename "$(shell pwd)")_caddy-data:/caddy-data:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file config/.env.client \
	-e FAME_SHOW_ENVELOPES=true \
	$(DOCKER_IMAGE) \
	python client.py

clean: stop
	@echo "🧹 Cleaning generated files..."
	@cd config && rm -rf .env.client .env.agent .env.oauth2-server .env.sentinel
	@echo "🧹 Cleaning secrets directory with Docker..."
	@docker run --rm -v "$(shell cd .. && pwd)/.secrets:/work/.secrets" alpine:latest sh -c "rm -rf /work/.secrets" 2>/dev/null || rm -rf ../.secrets 2>/dev/null || true
	@echo "🧹 Cleaning bind-mounted caddy data..."
	@docker run --rm -v "$(shell pwd)/config/caddy:/work/caddy" alpine:latest sh -c "rm -rf /work/caddy/data" 2>/dev/null || rm -rf config/caddy/data 2>/dev/null || true
	@echo "🧹 Removing Caddy named volume..."
	@docker volume rm "$(shell basename "$(shell pwd)")_caddy-data" 2>/dev/null || true
	@echo "✅ Cleaned generated .env files, secrets directory, caddy data, and named volume"
