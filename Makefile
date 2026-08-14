SHELL := /usr/bin/env bash

.PHONY: help lint lint-docs format test test-unit test-integration test-e2e clean

PY ?= python3
E2E_IMAGE ?= unit-suffix-remover-e2e
MD_LINT_IMAGE ?= davidanson/markdownlint-cli2:latest
MERMAID_IMAGE ?= minlag/mermaid-cli:latest

export PYTHONPATH := $(CURDIR)/src

help:
	@echo "Targets:"
	@echo "  make lint             - ruff check + ruff format --check"
	@echo "  make lint-docs        - markdownlint + mermaid diagram validation"
	@echo "  make format           - apply ruff format"
	@echo "  make test             - unit + integration tests"
	@echo "  make test-unit        - unit tests only"
	@echo "  make test-integration - integration tests only"
	@echo "  make test-e2e         - install and exercise the CLI in a container"
	@echo "  make clean            - remove caches"

lint:
	ruff check .
	ruff format --check .

# The repository is mounted read-only: mermaid-cli writes its SVGs next to the
# output file, which must never land in the working tree.
lint-docs:
	docker run --rm -v "$(CURDIR)":/workdir $(MD_LINT_IMAGE) "**/*.md"
	docker run --rm -v "$(CURDIR)":/data:ro -w /tmp $(MERMAID_IMAGE) -i /data/README.md -o /tmp/out.md

format:
	ruff format .

test: test-unit test-integration

test-unit:
	$(PY) -m unittest discover -s tests/unit -t . -p "test_*.py"

test-integration:
	$(PY) -m unittest discover -s tests/integration -t . -p "test_*.py"

test-e2e:
	docker build -f tests/e2e/Dockerfile -t $(E2E_IMAGE) .
	docker run --rm $(E2E_IMAGE)

clean:
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -type d -name "__pycache__" -print0 | xargs -0 -r rm -rf
