SHELL := /bin/bash

backend_image_name := github-analyzer-backend
venv_dir := venv

# Use the .env file to pull the GH_PAT
ifneq (,$(wildcard .env))
	include .env
	export
endif

.PHONY: all build check-env venv install precommit hooks create-image test trivy help

help:
	@echo "Available targets:"
	@echo "  build         - Setup local tooling (venv, deps, pre-commit, hooks, images) and start the compose services"
	@echo "  check-env     - No-op placeholder for compatibility"
	@echo "  venv          - Create Python virtual environment"
	@echo "  install       - Install Python dependencies"
	@echo "  precommit     - Install pre-commit hooks"
	@echo "  hooks         - Install git pre-push hooks"
	@echo "  create-image  - Build the compose service images"
	@echo "  test          - Run backend pytest in the backend container"
	@echo "  trivy         - Run Trivy security scan on backend image"
	@echo ""
	@echo "Prerequisites:"
	@echo "  - Python 3.x (for local tooling targets)"
	@echo "  - Docker with Compose"

build: check-env venv install precommit hooks create-image
	docker compose up --build

check-env:
	@echo "No required .env file for the current compose setup."

venv:
	python3 -m venv $(venv_dir)
	@. $(venv_dir)/bin/activate && echo "Virtual environment activated"

install:
	$(venv_dir)/bin/pip install -r backend/requirements.txt

precommit:
	$(venv_dir)/bin/pre-commit install

hooks:
	echo '#!/bin/sh' > .git/hooks/pre-push
	echo 'docker compose run --rm backend pytest || { echo "❌ Unit tests failed."; exit 1; }' >> .git/hooks/pre-push
	echo 'make trivy' >> .git/hooks/pre-push
	echo 'scan_exit_code=$$?' >> .git/hooks/pre-push
	echo 'if [ $$scan_exit_code -ne 0 ]; then' >> .git/hooks/pre-push
	echo '  echo "❌ Vulnerabilities found in image: $(backend_image_name)"' >> .git/hooks/pre-push
	echo '  exit $$scan_exit_code' >> .git/hooks/pre-push
	echo 'fi' >> .git/hooks/pre-push
	echo 'exit 0' >> .git/hooks/pre-push
	chmod ug+x .git/hooks/pre-push
	@echo "Git pre-push hook installed"

create-image:
	@echo "Creating docker images..."
	docker compose build

test:
	@echo "Running unit tests..."
	@docker compose run --rm backend pytest || { echo "❌ Unit tests failed."; exit 1; }
	@echo "✅ Unit tests passed."

trivy:
	@echo "Running Trivy security scan..."
	$(eval IMAGE_ID := $(shell docker images -q ${backend_image_name}:latest))
	@if [ -z "$(IMAGE_ID)" ]; then \
		echo "Error: Image not found for ${backend_image_name}. Make sure you've built the image."; \
		exit 1; \
	fi
	@docker run --rm \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(shell pwd)/.trivyignore:/tmp/.trivyignore \
		aquasec/trivy:0.70.0 \
		image \
		--scanners vuln \
		--exit-code 1 \
		--severity CRITICAL \
		--ignore-unfixed \
		"$(IMAGE_ID)" || { \
			echo "❌ Vulnerabilities found in image: $(backend_image_name)"; \
			exit 1; \
		}
	@echo "✅ Trivy scan passed. No critical/high vulnerabilities detected."
