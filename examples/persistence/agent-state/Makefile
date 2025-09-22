.DEFAULT_GOAL := start_with_init

init:
	@python3 ../../security/scripts/generate_dev_secrets.py --from-subdir

start:
	docker compose up -d

start_with_init: init
	docker compose up -d

stop:
	docker compose down --remove-orphans

run:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	-e FAME_SHOW_ENVELOPES=false \
	-e FAME_DIRECT_ADMISSION_URL="ws://sentinel:8000/fame/v1/attach/ws/downstream" \
	naylence/agent-sdk-python:0.3.14 \
	python client.py

run-verbose:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	-e FAME_SHOW_ENVELOPES=true \
	-e FAME_DIRECT_ADMISSION_URL="ws://sentinel:8000/fame/v1/attach/ws/downstream" \
	naylence/agent-sdk-python:0.3.14 \
	python client.py

clean: stop
	@echo "🧹 Cleaning generated files..."
	@cd config && rm -rf .env.client .env.agent .env.sentinel
	@echo "🧹 Cleaning secrets directory with Docker..."
	@docker run --rm -v "$(shell cd ../../security && pwd)/.secrets:/work/.secrets" alpine:latest sh -c "rm -rf /work/.secrets" 2>/dev/null || rm -rf ../../security/.secrets 2>/dev/null || true
	@echo "🧹 Cleaning data directory with Docker..."
	@docker run --rm -v "$(shell pwd)/data:/work/data" alpine:latest sh -c "rm -rf /work/data" 2>/dev/null || rm -rf data 2>/dev/null || true
	@echo "✅ Cleaned generated .env files, secrets directory, and data directory"