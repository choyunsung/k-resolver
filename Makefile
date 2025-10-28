.PHONY: help build up down logs shell db-shell migrate seed test lint format clean

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

build:  ## Build containers
	podman-compose build

up:  ## Start all services
	podman-compose up -d

down:  ## Stop all services
	podman-compose down

logs:  ## Show logs
	podman-compose logs -f

shell:  ## Open shell in API container
	podman-compose exec api bash

db-shell:  ## Open PostgreSQL shell
	podman-compose exec db psql -U kresolver -d kresolver

migrate:  ## Run database migrations
	podman-compose exec api alembic upgrade head

seed:  ## Seed initial data
	podman-compose exec api python scripts/seed_data.py

test:  ## Run tests
	podman-compose exec api pytest

test-cov:  ## Run tests with coverage
	podman-compose exec api pytest --cov=src --cov-report=html

lint:  ## Run linting
	podman-compose exec api ruff check src/

format:  ## Format code
	podman-compose exec api ruff format src/

mypy:  ## Run type checking
	podman-compose exec api mypy src/

clean:  ## Clean up containers and volumes
	podman-compose down -v
	rm -rf logs/*
