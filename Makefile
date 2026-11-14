.PHONY: install dev test lint run
install:
	python -m pip install -e .
dev:
	python -m pip install -e '.[dev,pdf]'
test:
	pytest
lint:
	ruff check app tests
run:
	uvicorn app.main:app --reload
