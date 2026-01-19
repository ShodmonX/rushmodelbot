.PHONY: help up down restart build rebuild logs logs-api logs-bot logs-worker ps \
	migrate makemigrations downgrade db-reset api-shell bot-shell psql \
	ngrok-url webhook-info curl-health lint format test seed \
	up-prod down-prod logs-prod

COMPOSE = docker compose
PROFILE_DEV = --profile dev
PROFILE_PROD = --profile prod
API_SERVICE = api
BOT_SERVICE = bot
WORKER_SERVICE = worker
DB_SERVICE = db
ENV_FILE = .env

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z0-9_-]+:.*##/ {printf "%-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start dev services with ngrok
	$(COMPOSE) $(PROFILE_DEV) up -d --build

down: ## Stop services
	$(COMPOSE) down

restart: ## Restart services
	$(MAKE) down
	$(MAKE) up

build: ## Build services
	$(COMPOSE) build

rebuild: ## Rebuild services without cache
	$(COMPOSE) build --no-cache

logs: ## Follow all logs
	$(COMPOSE) logs -f --tail=200

logs-api: ## Follow API logs
	$(COMPOSE) logs -f --tail=200 $(API_SERVICE)

logs-bot: ## Follow bot logs
	$(COMPOSE) logs -f --tail=200 $(BOT_SERVICE)

logs-worker: ## Follow worker logs (if exists)
	$(COMPOSE) logs -f --tail=200 $(WORKER_SERVICE) || echo "worker service not defined"

ps: ## Show service status
	$(COMPOSE) ps

migrate: ## Apply alembic migrations
	$(COMPOSE) exec $(API_SERVICE) alembic upgrade head

makemigrations: ## Create migration, e.g. make makemigrations msg="init"
	$(COMPOSE) exec $(API_SERVICE) alembic revision --autogenerate -m "$(msg)"

downgrade: ## Downgrade last migration
	$(COMPOSE) exec $(API_SERVICE) alembic downgrade -1

db-reset: ## Drop volumes, start fresh, and migrate
	$(COMPOSE) down -v
	$(MAKE) up
	$(MAKE) migrate

api-shell: ## Open shell in API container
	$(COMPOSE) exec $(API_SERVICE) sh

bot-shell: ## Open shell in bot container
	$(COMPOSE) exec $(BOT_SERVICE) sh

psql: ## Open psql in DB container
	$(COMPOSE) exec $(DB_SERVICE) psql -U postgres -d rushmodelbot

ngrok-url: ## Print ngrok public HTTPS URL
	@curl -s http://localhost:4040/api/tunnels | \
	python - <<'PY'\nimport json,sys\npayload=json.load(sys.stdin)\nurl=None\nfor t in payload.get(\"tunnels\", []):\n    public=t.get(\"public_url\")\n    if isinstance(public,str) and public.startswith(\"https://\"):\n        url=public\n        break\nprint(url or \"No HTTPS tunnel found\")\nPY

webhook-info: ## Show Telegram webhook info (dev)
	@sh -c 'set -a; \
	if [ -f "$(ENV_FILE)" ]; then . "./$(ENV_FILE)"; else echo "$(ENV_FILE) not found"; exit 1; fi; \
	set +a; \
	if [ -z "$$BOT_TOKEN" ]; then echo "BOT_TOKEN is missing in $(ENV_FILE)"; exit 1; fi; \
	curl -s "https://api.telegram.org/bot$$BOT_TOKEN/getWebhookInfo"'

curl-health: ## Check API health endpoint
	@curl -s http://localhost:8000/health

lint: ## Run linter (ruff)
	$(COMPOSE) exec $(API_SERVICE) ruff check .

format: ## Run formatter (ruff format)
	$(COMPOSE) exec $(API_SERVICE) ruff format .

test: ## Run tests
	$(COMPOSE) exec $(API_SERVICE) pytest

seed: ## Seed data (placeholder)
	@echo "Seed not implemented yet"

up-prod: ## Start prod services
	$(COMPOSE) $(PROFILE_PROD) up -d --build

down-prod: ## Stop prod services
	$(COMPOSE) $(PROFILE_PROD) down

logs-prod: ## Follow prod logs
	$(COMPOSE) $(PROFILE_PROD) logs -f --tail=200
