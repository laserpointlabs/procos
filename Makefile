# ProcOS Makefile

# Load .env if present
ifneq (,$(wildcard ./.env))
include .env
export
endif

.PHONY: help up down stop stack-start stack-stop start status logs test lint format health pytest

help:
	@echo "Targets:"
	@echo "  up            - docker compose up -d --build"
	@echo "  down          - docker compose down"
	@echo "  stop          - docker compose stop"
	@echo "  stack-start   - same as up"
	@echo "  stack-stop    - same as stop"
	@echo "  start         - ./procos.sh start"
	@echo "  status        - ./procos.sh status"
	@echo "  logs          - ./procos.sh logs -f"
	@echo "  test          - ./procos.sh test"
	@echo "  health        - python scripts/health_check.py"
	@echo "  pytest        - run unit tests"
	@echo "  lint          - ruff/flake8 if available"
	@echo "  format        - black if available"

up stack-start:
	docker compose up -d --build

stop stack-stop:
	docker compose stop

down:
	docker compose down

start:
	./procos.sh start

status:
	./procos.sh status

logs:
	./procos.sh logs -f

test:
	./procos.sh test

health:
	python3 scripts/health_check.py || true

lint:
	-ruff check || true
	-flake8 || true

format:
	-black . || true

pytest:
	pytest -q || true


