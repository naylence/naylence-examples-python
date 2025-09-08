.DEFAULT_GOAL := start

init:
	@python3 ../../security/scripts/generate_dev_secrets.py --from-subdir

start: init
	docker compose up -d

stop:
	docker compose down --remove-orphans

run:
	@python client.py

run-verbose:
	@FAME_SHOW_ENVELOPES=true python client.py

clean: stop
	@echo "🧹 Cleaning generated files..."
	@cd config && rm -rf .env.client .env.agent .env.oauth2-server .env.sentinel
	@rm -rf ../.secrets
	@rm -rf config/caddy/data
	@echo "✅ Cleaned generated .env files and secrets directory"
