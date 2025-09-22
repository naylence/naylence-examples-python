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
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	-e FAME_SHOW_ENVELOPES=false \
	-e FAME_DIRECT_ADMISSION_URL="ws://echo-agent:8000/fame/v1/attach/ws/downstream" \
	naylence/agent-sdk-python:0.3.14 \
	python client.py

run-docker-verbose:
	@docker run --rm \
	-v "$(shell pwd):/work:ro" \
	-w /work \
	--network "$(shell basename "$(shell pwd)")_naylence-net" \
	-e FAME_SHOW_ENVELOPES=true \
	-e FAME_DIRECT_ADMISSION_URL="ws://echo-agent:8000/fame/v1/attach/ws/downstream" \
	naylence/agent-sdk-python:0.3.14 \
	python client.py

clean: stop
	@echo "🧹 Nothing to clean"
