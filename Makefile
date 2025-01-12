MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(dir $(MAKEFILE_PATH))
HOME_PATH := $(MAKEFILE_DIR)
VENV_PATH ?= $(HOME_PATH)/.venv

PYTHON ?= PYTHONPATH=$(HOME_PATH) $(VENV_PATH)/bin/python
SYSTEM_PYTHON ?= python3

SRCFILES := ic

venv: ##
	test -d $(VENV_PATH) || $(SYSTEM_PYTHON) -m venv $(VENV_PATH) --clear
	$(PYTHON) -m pip install --requirement requirements.txt
	$(PYTHON) -m pip install --requirement requirements-dev.txt

format:  ##
	$(PYTHON) -m black $(SRCFILES)
	$(PYTHON) -m isort --profile black $(SRCFILES)

lint:  ##
	$(PYTHON) -m black --check $(SRCFILES)
	$(PYTHON) -m ruff check $(SRCFILES)

clear:  ##
	rm -rvf $(SRCFILES)/**/*.pyc
	rm -rvf $(SRCFILES)/**/__pycache__

demo: DEMODIR := $(shell mktemp -d)
demo:
	dd if=/dev/random of=$(DEMODIR)/demo.data bs=1048576 count=1
	@ls -l $(DEMODIR)/demo.data
	@md5sum $(DEMODIR)/demo.data

	$(PYTHON) -m ic $(DEMODIR)/demo.data $(DEMODIR)/demo.png
	@ls -lh $(DEMODIR)/demo.png
	-@identify $(DEMODIR)/demo.png

	$(PYTHON) -m ic -d $(DEMODIR)/demo.png $(DEMODIR)/demo-out.data
	@ls -l $(DEMODIR)/demo-out.data
	@md5sum $(DEMODIR)/demo-out.data

	@convert $(DEMODIR)/demo.png -bordercolor Yellow -border 12x34 $(DEMODIR)/demo-pp.png
	-@identify $(DEMODIR)/demo-pp.png
	$(PYTHON) -m ic -d -a $(DEMODIR)/demo-pp.png $(DEMODIR)/demo-pp.data
	@ls -l $(DEMODIR)/demo-pp.data
	@md5sum $(DEMODIR)/demo-pp.data

	@rm -rfv $(DEMODIR)/demo*
	@rm -rfv $(DEMODIR)


