format:
	poetry run black .

run:
	uvicorn server.main:app --reload

test:
	poetry run pytest --cov server --cov-report term-missing -v -s tests -m 'not expensive'

test-all:
	poetry run pytest --cov server --cov-report term-missing -v -s tests

initdb:
	python -c 'from server.database import init_db; init_db()'