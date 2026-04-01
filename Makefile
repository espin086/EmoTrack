.PHONY: help setup install clean start-standalone start-backend start-frontend stop test lint format

help: ## Show this help message
	@echo "EmoTrack - Local Development Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - create venv and install dependencies
	@echo "Setting up EmoTrack..."
	python3 -m venv venv
	@echo "Virtual environment created"
	@echo "Run 'make install' to install dependencies"

install: ## Install dependencies (run after activating venv)
	@echo "Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements-local.txt
	@echo "Dependencies installed"

clean: ## Remove virtual environment and cache files
	@echo "Cleaning up..."
	rm -rf venv
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf *.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete"

start-standalone: ## Start standalone mode (simplest)
	@echo "Starting EmoTrack Standalone..."
	streamlit run EmoTrack.py --server.port 8501 --server.address localhost

start-backend: ## Start backend API (Full Stack mode)
	@echo "Starting Backend..."
	cd backend && DB_PATH=../data/emotions.db python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

start-frontend: ## Start frontend (Full Stack mode)
	@echo "Starting Frontend..."
	cd frontend && BACKEND_URL=http://localhost:8000 streamlit run app.py --server.port 8501 --server.address localhost

stop: ## Stop all EmoTrack processes
	@echo "Stopping EmoTrack..."
	-lsof -ti:8501 | xargs kill -9 2>/dev/null || true
	-lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@echo "All processes stopped"

test: ## Run all tests
	@echo "Running tests..."
	pytest tests/test_model.py logic/test_facial_analysis.py backend/test_app.py -v

test-model: ## Run ONNX model tests only
	@echo "Running model tests..."
	pytest tests/test_model.py -v

test-facial: ## Run facial analysis tests only
	@echo "Running facial analysis tests..."
	pytest logic/test_facial_analysis.py -v

test-backend: ## Run backend API tests only
	@echo "Running backend tests..."
	pytest backend/test_app.py -v

create-model: ## Generate ONNX emotion detection model
	@echo "Creating ONNX model..."
	python models/create_model.py
	@echo "Model created at models/emotion_model.onnx"

lint: ## Run linters
	@echo "Running linters..."
	pylint backend/app.py frontend/app.py EmoTrack.py logic/facial_analysis.py

format: ## Format code with black
	@echo "Formatting code..."
	black backend/app.py frontend/app.py EmoTrack.py logic/facial_analysis.py

db-backup: ## Backup emotions database
	@echo "Backing up database..."
	@mkdir -p backups
	@if [ -f emotions.db ]; then \
		cp emotions.db backups/emotions_$(shell date +%Y%m%d_%H%M%S).db; \
		echo "Backed up emotions.db"; \
	fi
	@if [ -f data/emotions.db ]; then \
		cp data/emotions.db backups/emotions_fullstack_$(shell date +%Y%m%d_%H%M%S).db; \
		echo "Backed up data/emotions.db"; \
	fi

db-clear: ## Clear emotions database (WARNING: deletes all data)
	@echo "WARNING: This will delete all emotion data!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f emotions.db data/emotions.db; \
		echo "Database cleared"; \
	else \
		echo "Cancelled"; \
	fi

logs: ## Show recent logs (if any)
	@echo "Recent logs..."
	@tail -n 50 *.log 2>/dev/null || echo "No log files found"

status: ## Check if services are running
	@echo "Service Status..."
	@echo "Backend (port 8000):"
	@lsof -ti:8000 > /dev/null 2>&1 && echo "  Running" || echo "  Not running"
	@echo "Frontend (port 8501):"
	@lsof -ti:8501 > /dev/null 2>&1 && echo "  Running" || echo "  Not running"

camera-test: ## Test camera access
	@echo "Testing camera access..."
	@python3 -c "import cv2; cap = cv2.VideoCapture(0); ret, _ = cap.read(); cap.release(); print('Camera working!' if ret else 'Camera failed')"

requirements: ## Generate/update requirements-local.txt
	@echo "Generating requirements..."
	pip freeze > requirements-local.txt
	@echo "requirements-local.txt updated"

dev: ## Development mode - start both backend and frontend with auto-reload
	@echo "Starting development mode..."
	@make -j 2 start-backend start-frontend

build-macos: ## Build macOS .app bundle via Tauri (requires Rust + Tauri CLI)
	@echo "Building macOS app bundle..."
	@echo "Prerequisites: brew install rust && cargo install tauri-cli"
	@echo "Run: cargo tauri build"
	@echo "Output: target/release/bundle/macos/EmoTrack.app"

.DEFAULT_GOAL := help
