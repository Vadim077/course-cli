.PHONY: install test coverage

install:
	pip install -e .

test:
	pytest tests/

coverage:
	pytest --cov=course_cli --cov-report=term --cov-report=html

docker-build:
	docker compose build

docker-up:
	docker compose run --rm cli --help