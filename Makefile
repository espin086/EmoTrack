# Makefile for EmoTrack

# Docker commands
.PHONY: build up down logs clean migrate help setup black-it pylint pytest isort all

# Build Docker images
build:
	docker-compose build

# Start services
up:
	docker-compose up -d

# Start services with build
up-build:
	docker-compose up -d --build

# Stop services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# View backend logs
logs-backend:
	docker-compose logs -f backend

# View frontend logs  
logs-frontend:
	docker-compose logs -f frontend

# Clean up containers, volumes, and images
clean:
	docker-compose down -v --rmi all
	rm -rf data/

# Migrate existing data
migrate:
	python3 migrate_data.py

# Run locally (development)
dev-backend:
	cd backend && pip install -r requirements.txt && uvicorn app:app --reload

dev-frontend:
	cd frontend && pip install -r requirements.txt && streamlit run app.py

# Python development commands
setup:
	python3 -m pip install --upgrade pip
	pip install flake8 pytest pylint black isort
	if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Check Black formatting
black-it:
	black .

# Lint with Pylint
pylint:
	pylint **/*.py

# Run Pytest
pytest:
	pytest

# Sort imports with isort
isort:
	isort **/*.py

# All-in-one command to run all checks
all: setup isort black-it pylint pytest

# Help
help:
	@echo "EmoTrack Makefile Commands:"
	@echo ""
	@echo "Docker Commands:"
	@echo "  make build         - Build Docker images"
	@echo "  make up            - Start all services"
	@echo "  make up-build      - Build and start services"
	@echo "  make down          - Stop all services"
	@echo "  make logs          - View all logs"
	@echo "  make logs-backend  - View backend logs"
	@echo "  make logs-frontend - View frontend logs"
	@echo "  make clean         - Clean up containers and volumes"
	@echo "  make migrate       - Migrate existing database"
	@echo ""
	@echo "Development Commands:"
	@echo "  make dev-backend   - Run backend locally"
	@echo "  make dev-frontend  - Run frontend locally"
	@echo "  make setup         - Set up Python environment"
	@echo "  make black-it      - Format code with Black"
	@echo "  make pylint        - Lint with Pylint"
	@echo "  make pytest        - Run tests"
	@echo "  make isort         - Sort imports"
	@echo "  make all           - Run all Python checks"
