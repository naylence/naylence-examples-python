.DEFAULT_GOAL := start

init:
	@python3 ../../security/scripts/generate_dev_secrets.py --from-subdir

start: init
	docker compose up -d

stop:
	docker compose down --remove-orphans

run:
	@FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream" \
	python client.py
	@echo
	@echo "Waiting a few seconds for message-agent to process..."
	@sleep 5
	@echo "Message-agent logs:"
	@docker compose logs message-agent

run-verbose:
	@FAME_SHOW_ENVELOPES=true \
	FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream" \
	python client.py
	@echo
	@echo "Waiting a few seconds for message-agent to process..."
	@sleep 5
	@echo "Message-agent logs:"
	@docker compose logs message-agent

logs:
	@echo "Tailing message-agent logs (press Ctrl+C to stop)..."
	docker compose logs -f -t --tail=100 message-agent

clean: stop
	@echo "🧹 Cleaning generated files..."
	@rm -rf ../../security/.secrets
	@rm -rf config/.env.agent
	@rm -rf data
	@echo "✅ Cleaned generated .env files and secrets directory"
