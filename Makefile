PYTHON   = python3
VENV     = .venv
PIP      = $(VENV)/bin/pip
MAIN     = a_maze_ing.py
CONFIG   = config.txt

.PHONY: install run debug lint lint-strict clean

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run:
	$(VENV)/bin/python $(MAIN) $(CONFIG)

debug:
	$(VENV)/bin/python -m pdb $(MAIN) $(CONFIG)

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --strict

clean:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache