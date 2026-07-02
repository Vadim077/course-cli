.PHONY: install test coverage docker-build docker-up run-cli demo

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

run-cli:
	@echo "Start Course CLI..."
	course-cli --help

demo:
	@echo "Running demonstration scenario..."
	@rm -rf DemoCourse
	@echo "1. Initializing course"
	course-cli init DemoCourse
	@echo "2. Validating course..."
	-course-cli validate DemoCourse
	@echo "3. Generating report..."
	course-cli report DemoCourse
	@echo "Demonstration completed."