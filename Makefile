install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

build:
	./build.sh

package-install:
	python3 -m pip install --user dist/*.whl

lint:
	uv run flake8 page_analyzer

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app