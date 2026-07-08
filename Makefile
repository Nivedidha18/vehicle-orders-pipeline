.PHONY: install run test clean

install:
	pip install -r requirements.txt

run:
	python -m src.pipeline.run

test:
	pytest -q

clean:
	rm -rf build __pycache__ .pytest_cache
