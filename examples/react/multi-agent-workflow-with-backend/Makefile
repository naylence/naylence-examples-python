.DEFAULT_GOAL := start

build:
	docker compose build

start: build
	docker compose up -d

stop:
	docker compose down --remove-orphans

logs:
	docker compose logs -f

run-browser:
	@echo "📦 Installing frontend dependencies..."
	@cd browser && npm install
	@echo "🚀 Starting frontend dev server..."
	@cd browser && npm run dev

clean: stop
	@echo "🧹 Cleaning up containers..."
	docker compose down --remove-orphans --volumes

.PHONY: build start stop logs run-frontend clean
