.PHONY: help install setup test run-pipeline run-dashboard clean

help:
	@echo "Gaming Data Pipeline - Makefile Commands"
	@echo ""
	@echo "  make install     - Install dependencies"
	@echo "  make setup       - Set up project (directories, database)"
	@echo "  make test        - Run test suite"
	@echo "  make run-pipeline - Run ETL pipeline"
	@echo "  make run-dashboard - Start Streamlit dashboard"
	@echo "  make clean       - Clean temporary files"

install:
	pip install -r requirements.txt

setup:
	python setup.py

test:
	pytest tests/ -v

run-pipeline:
	python src/etl/run_pipeline.py

run-dashboard:
	python -m streamlit run dashboard/app.py

clean:
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
