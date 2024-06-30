.DEFAULT_GOAL := up

lint:
	@echo "Running linter"
	black .
	ruff check .

up:
	@echo "Starting the server"
	docker-compose up -d --build
