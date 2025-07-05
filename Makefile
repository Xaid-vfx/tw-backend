.PHONY: dev install clean

dev:
	source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

install:
	python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

clean:
	rm -rf venv/ __pycache__/ .pytest_cache/ .coverage 