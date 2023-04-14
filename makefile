format:
	poetry run black .

run:
	uvicorn server.main:app --reload

test:
	poetry run pytest --cov server --cov-report term-missing -v -s tests