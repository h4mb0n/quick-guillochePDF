VENV   := .venv
PYTHON := $(VENV)/bin/python

.PHONY: setup

setup:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --quiet --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
