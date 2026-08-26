.PHONY: workbench api test build
workbench:
	./scripts/start_workbench.sh
api:
	PYTHONPATH=src python3 -m uvicorn services.api.app:app --host 127.0.0.1 --port 8000
test:
	python3 -m unittest discover -s tests -v
	PYTHONPATH=src python3 -m pytest tests/test_v040_dense_index_builder.py -v
build:
	python3 -m build
