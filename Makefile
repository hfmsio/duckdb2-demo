PYTHON ?= python3
VENV   := .venv/bin/python

.PHONY: demo recipes
demo: $(VENV)
	$(VENV) desk/run.py $(ARGS)

recipes: $(VENV)
	$(VENV) recipes/run.py $(ARGS)

$(VENV):
	@$(PYTHON) -c 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else "DuckDB 2.0 needs Python 3.11+. Try: make PYTHON=python3.12")'
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -q -r requirements.txt
