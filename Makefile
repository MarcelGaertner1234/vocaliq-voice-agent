# VocalIQ Makefile
SHELL := /bin/bash

.PHONY: help up down logs test clean setup

# Default target
help:
	@echo "VocalIQ Development Commands:"
	@echo "  make setup     - Initial project setup"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - Show API logs"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Clean up containers and volumes"
	@echo "  make db-init   - Initialize database"
	@echo "  make ngrok     - Start ngrok tunnel"
	@echo ""
	@echo "Production Commands:"
	@echo "  make up-prod   - Start production environment"
	@echo "  make down-prod - Stop production environment"
	@echo "  make backup    - Create database backup"

# Development Commands
setup:
	@echo "Setting up VocalIQ..."
	@cp -n env.example .env || true
	@mkdir -p backend/logs backend/storage
	@echo "Setup complete! Edit .env file and run 'make up'"

up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f api

test:
	docker compose exec api pytest -v

clean:
	docker compose down -v
	rm -rf backend/__pycache__ backend/.pytest_cache
	find . -name "*.pyc" -delete

# Database Commands
db-init:
	docker compose exec api alembic upgrade head
	docker compose exec api python scripts/seed_database.py

db-migrate:
	docker compose exec api alembic revision --autogenerate -m "$(message)"

db-upgrade:
	docker compose exec api alembic upgrade head

db-downgrade:
	docker compose exec api alembic downgrade -1

# Production Commands
up-prod:
	docker compose -f docker-compose.prod.yml up --build -d

down-prod:
	docker compose -f docker-compose.prod.yml down

logs-prod:
	docker compose -f docker-compose.prod.yml logs -f

# Utility Commands
ngrok:
	ngrok http 8000

shell-api:
	docker compose exec api /bin/bash

shell-db:
	docker compose exec postgres psql -U vocaliq -d vocaliq

redis-cli:
	docker compose exec redis redis-cli

# Monitoring
monitoring-up:
	docker compose --profile monitoring up -d

monitoring-down:
	docker compose --profile monitoring down

# Testing specific services
test-unit:
	docker compose exec api pytest tests/unit -v

test-integration:
	docker compose exec api pytest tests/integration -v

test-coverage:
	docker compose exec api pytest --cov=api --cov-report=html

# Linting and formatting
lint:
	docker compose exec api ruff check .
	docker compose exec api mypy api/

format:
	docker compose exec api black .
	docker compose exec api ruff check --fix .

# Build commands
build-api:
	docker build -t vocaliq/api:latest ./backend

build-frontend:
	docker build -t vocaliq/frontend:latest ./backend/frontend

# Backup
backup:
	@mkdir -p backups
	@docker compose exec postgres pg_dump -U vocaliq vocaliq | gzip > backups/vocaliq_$(shell date +%Y%m%d_%H%M%S).sql.gz
	@echo "Backup created: backups/vocaliq_$(shell date +%Y%m%d_%H%M%S).sql.gz"

restore:
	@echo "Restoring from $(file)..."
	@gunzip -c $(file) | docker compose exec -T postgres psql -U vocaliq vocaliq

# Development helpers
dev-install:
	pip install -r requirements.txt
	npm install --prefix backend/frontend

dev-api:
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	cd backend/frontend && npm run dev

# Documentation
docs-serve:
	mkdocs serve -f docs/mkdocs.yml

docs-build:
	mkdocs build -f docs/mkdocs.yml

# Quick commands
restart: down up

rebuild: clean up

status:
	docker compose ps

version:
	@echo "VocalIQ Development Environment v1.0.0"