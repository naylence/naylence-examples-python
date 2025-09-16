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
	@FAME_SHOW_ENVELOPES=false \
	FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream" \
	python client.py

run-verbose:
	@FAME_SHOW_ENVELOPES=true \
	FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream" \
	python client.py

clean: stop
	@echo "🧹 Cleaning generated files..."
	@cd config && rm -rf .env.client .env.agent .env.sentinel
	@rm -rf ../../security/.secrets
	@rm -rf data
	@echo "✅ Cleaned generated .env files and secrets directory"