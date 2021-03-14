test: verify_format lint

format:
	isort .
	black .

verify_format:
	black --check .

lint:
	flake8 .