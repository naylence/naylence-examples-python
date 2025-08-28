.DEFAULT_GOAL := all

all: up run-client

init:
	python3 ../scripts/generate_dev_secrets.py --from-subdir

up: init
	docker compose up -d

down:
	docker compose down --remove-orphans

run-client:
	python client.py

clean:
	@echo "🧹 Cleaning generated files..."
	@rm -f .env.client .env.agent .env.oauth2-server .env.sentinel
	@rm -rf ../.secrets
	@echo "✅ Cleaned generated .env files and secrets directory"
