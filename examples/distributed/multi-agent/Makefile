.DEFAULT_GOAL := start

build:
	docker compose build

start: build
	docker compose up -d

stop:
	docker compose down --remove-orphans

run:
	@FAME_SHOW_ENVELOPES=false \
	FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream" \
	poetry run python client.py

run-verbose:
	@FAME_SHOW_ENVELOPES=true \
	FAME_DIRECT_ADMISSION_URL="ws://localhost:8000/fame/v1/attach/ws/downstream" \
	poetry run python client.py

clean: stop
	@echo "🧹 Nothing to clean"
