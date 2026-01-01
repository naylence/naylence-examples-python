# Docker image for Naylence Agent SDK
DOCKER_IMAGE := naylence/agent-sdk-adv-python:0.4.8

.DEFAULT_GOAL := start

init:
	@echo "🔐 Generating PKI certificates..."
	@docker run --rm \
		-v "$(shell pwd):/work" \
		-w /work \
		$(DOCKER_IMAGE) \
		python -m naylence.fame.security.cert.setup_pki --output ./config/certs --org "Strict Overlay Development"
	
	@echo "🔑 Generating dev secrets..."
	@docker run --rm \
		-v "$(shell pwd)/../..:/work" \
		-w /work/$(shell basename "$(shell dirname "$(shell pwd)")")/$(shell basename "$(shell pwd)") \
		$(DOCKER_IMAGE) \
		python ../scripts/generate_dev_secrets.py --from-subdir


start: init
	docker compose up -d

stop:
	docker compose down --remove-orphans

run:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-v ./config/certs:/etc/fame/certs \
	-v "$(shell basename "$(shell pwd)")_caddy-data:/caddy-data:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file config/.env.client \
	$(DOCKER_IMAGE) \
	python client.py

run-verbose:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-v ./config/certs:/etc/fame/certs \
	-v "$(shell basename "$(shell pwd)")_caddy-data:/caddy-data:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file config/.env.client \
	-e FAME_SHOW_ENVELOPES=true \
	$(DOCKER_IMAGE) \
	python client.py

clean: stop
	@echo "🧹 Cleaning generated files..."
	@cd config && rm -rf .env.client .env.agent .env.oauth2-server .env.sentinel .env.welcome .env.ca .env.policy
	@echo "🧹 Cleaning secrets directory with Docker..."
	@docker run --rm \
		-v "$(shell pwd)/../..:/work" \
		-w /work \
		$(DOCKER_IMAGE) \
		rm -rf ./security/.secrets 2>/dev/null || true
	@echo "🧹 Cleaning PKI certificates with Docker..."
	@docker run --rm \
		-v "$(shell pwd):/work" \
		-w /work \
		$(DOCKER_IMAGE) \
		rm -rf ./config/certs 2>/dev/null || true
	@rm -rf config/caddy/data
	@echo "✅ Cleaned generated .env files, PKI directory, and secrets directory"
