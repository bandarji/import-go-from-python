.DEFAULT_GOAL := help

IMAGE := gonpypoc

.PHONY: help docker-build docker-run docker-shell docker-test

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

docker-build: ## Build the Docker image
	docker build -t $(IMAGE) .

docker-run: docker-build ## Run the Python program in a Docker container
	docker run --rm $(IMAGE)

docker-shell: docker-build ## Open an interactive shell in a Docker container
	docker run --rm -it -e UV_NO_DEV=0 --entrypoint bash $(IMAGE)

docker-test: docker-build ## Run pytest in a Docker container
	docker run --rm -e UV_NO_DEV=0 --entrypoint bash $(IMAGE) -c \
		'uv sync --locked --no-editable && uv run pytest -v'
