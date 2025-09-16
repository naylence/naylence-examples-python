.DEFAULT_GOAL := start

init:
	

start: init
	docker compose up -d

stop:
	docker compose down --remove-orphans

run:
	@echo "Running client to send a message (with retries on no ACK received)..."
	@set -a; . config/.env.client; set +a; python client.py
	@echo
	@echo "Message-agent logs:"
	@docker compose logs message-agent

run-verbose:
	@echo "Running client to send a message (with retries on no ACK received)..."
	@set -a; . config/.env.client; set +a; FAME_SHOW_ENVELOPES=true python client.py
	@echo
	@echo "Message-agent logs:"
	@docker compose logs message-agent

logs:
	@echo "Tailing message-agent logs (press Ctrl+C to stop)..."
	docker compose logs -f -t --tail=100 message-agent

clean: stop
	
