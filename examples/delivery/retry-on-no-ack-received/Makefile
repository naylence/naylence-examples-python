.DEFAULT_GOAL := start

init:
	

start: init
	docker compose up -d

stop:
	docker compose down --remove-orphans

run:
	@echo "Running client to send a message (with retries on no ACK received)..."
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file config/.env.client \
	naylence/agent-sdk-python:0.3.14 \
	python client.py
	@echo
	@echo "Message-agent logs:"
	@docker compose logs message-agent

run-verbose:
	@echo "Running client to send a message (with retries on no ACK received)..."
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	--env-file config/.env.client \
	-e FAME_SHOW_ENVELOPES=true \
	naylence/agent-sdk-python:0.3.14 \
	python client.py
	@echo
	@echo "Message-agent logs:"
	@docker compose logs message-agent

logs:
	@echo "Tailing message-agent logs (press Ctrl+C to stop)..."
	docker compose logs -f -t --tail=100 message-agent

clean: stop
	@echo "🧹 Cleaning generated files..."
	@echo "🧹 Cleaning data directory with Docker..."
	@docker run --rm -v "$(shell pwd)/data:/work/data" alpine:latest sh -c "rm -rf /work/data" 2>/dev/null || rm -rf data 2>/dev/null || true
	@echo "✅ Cleaned data directory"
