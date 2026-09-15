.PHONY: help install dev prod test lint format clean docker-build docker-up docker-down migrate

help:
	@echo "BTC Algo Trading Platform - Available Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Set up development environment"
	@echo ""
	@echo "Running:"
	@echo "  make run           - Run application (development)"
	@echo "  make prod          - Run application (production)"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker images"
	@echo "  make docker-up     - Start Docker containers (dev)"
	@echo "  make docker-down   - Stop Docker containers"
	@echo "  make docker-logs   - View container logs"
	@echo ""
	@echo "Database:"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migrate-down  - Rollback database migrations"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test          - Run all tests"
	@echo "  make test-unit     - Run unit tests only"
	@echo "  make test-int      - Run integration tests only"
	@echo "  make coverage      - Generate coverage report"
	@echo "  make lint          - Run linters (flake8, mypy)"
	@echo "  make format        - Format code (black, isort)"
	@echo "  make check         - Run all checks (lint + test)"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean         - Clean up temporary files"
	@echo "  make clean-all     - Full cleanup including cache"

# Setup
install:
	pip install -r requirements.txt

dev: install
	cp .env.example .env
	docker-compose up -d
	alembic upgrade head
	@echo "Development environment ready!"

# Running
run:
	python src/main.py

prod:
	gunicorn -w 4 -b 0.0.0.0:8000 src.main:app

# Docker
docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f app

# Database
migrate:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

migrate-create:
	alembic revision --autogenerate -m "$(NAME)"

# Testing
test:
	pytest tests/ -v

test-unit:
	pytest tests/unit/ -v

test-int:
	pytest tests/integration/ -v

coverage:
	pytest --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

# Quality
lint:
	flake8 src tests --max-line-length=100
	mypy src --ignore-missing-imports

format:
	black src tests
	isort src tests

check: lint test
	@echo "All checks passed!"

# Cleanup
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	find . -type d -name '*.egg-info' -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov

clean-all: clean
	rm -rf venv .env
	docker-compose down -v
