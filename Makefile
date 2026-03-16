PYTHONPATH = PYTHONPATH=./
RUN =$(PYTHONPATH) poetry run
TEST = $(RUN) pytest
POETRY_RUN = poetry run

.PHONY: help
help: ##Show available commands
	@echo "Available commands: "
	@echo "   make install  - download dependencies"
	@echo "   make format   - refactor your code"
	@echo "   make lint     - start linter"
	@echo "   make test     - start tests"

.PHONY: install
install: ##install all dependencies
	poetry install --no-interaction --no-ansi --no-root --all-extras

.PHONY: format
format: ##refactoring code with linters
	$(POETRY_RUN) black ./src ./tests
	$(POETRY_RUN) ruff check --fix ./src ./tests
	$(POETRY_RUN) mypy ./src ./tests
	$(POETRY_RUN) pytest --dead-fixtures --dup-fixtures

.PHONY: lint
lint: ##Checking code with linters
	$(POETRY_RUN) black --check ./src ./tests
	$(POETRY_RUN) ruff check ./src ./tests
	$(POETRY_RUN) mypy ./src ./tests
	$(POETRY_RUN) pytest --dead-fixtures --dup-fixtures

.PHONY: test
test: ##test code with coverage
	$(TEST) tests/ --cov=src --cov-report json --cov-report term --cov-report xml:cobertura.xml
