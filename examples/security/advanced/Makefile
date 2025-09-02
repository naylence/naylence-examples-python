# Docker image for Naylence Agent SDK
DOCKER_IMAGE := naylence/agent-sdk-adv-python:0.1.17

.DEFAULT_GOAL := start

init:
	@echo "🔐 Generating PKI certificates..."
	@docker run --rm \
		-v "$(shell pwd):/work" \
		-w /work \
		$(DOCKER_IMAGE) \
		python -m naylence.fame.security.cert.setup_pki --output ./certs --org "Strict Overlay Development"
	@echo "🔑 Generating dev secrets..."
	@python3 ../scripts/generate_dev_secrets.py --from-subdir


start: init
	docker compose up -d

stop:
	docker compose down --remove-orphans

run:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-v ./certs:/etc/fame/certs \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file .env.client \
	$(DOCKER_IMAGE) \
	python client.py

run-verbose:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-v ./certs:/etc/fame/certs \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file .env.client \
	-e FAME_SHOW_ENVELOPES=true \
	$(DOCKER_IMAGE) \
	python client.py

clean: stop
	@echo "🧹 Cleaning generated files..."
	@rm -rf .env.client .env.agent .env.oauth2-server .env.sentinel .env.welcome .env.ca
	@rm -rf ../.secrets
	@rm -rf certs
	@rm -rf caddy/data
	@echo "✅ Cleaned generated .env files, PKI directory, and secrets directory"
