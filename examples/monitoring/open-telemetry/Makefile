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
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file config/.env.client \
	$(DOCKER_IMAGE) \
	python client.py

run-verbose:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-v "$(shell pwd)/config/client-config.yml:/etc/fame/fame-config.yml:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file config/.env.client \
	-e FAME_SHOW_ENVELOPES=true \
	$(DOCKER_IMAGE) \
	python client.py

clean: stop
	@echo "🧹 Cleaning generated files..."
	@cd config && rm -rf .env.client .env.agent .env.oauth2-server .env.sentinel
	@rm -rf ../.secrets
	@rm -rf config/caddy/data
	@echo "✅ Cleaned generated .env files and secrets directory"
