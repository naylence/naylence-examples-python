.DEFAULT_GOAL := start

start:
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

run-docker:
	@docker compose run --rm -e FAME_SHOW_ENVELOPES=false \
	client

run-docker-verbose:
	@docker compose run --rm -e FAME_SHOW_ENVELOPES=true \
	client

clean: stop
	@echo "🧹 Nothing to clean"
