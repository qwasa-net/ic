MAKEFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))
MAKEFILE_DIR := $(dir $(MAKEFILE_PATH))
HOME_PATH := $(MAKEFILE_DIR)
VENV_PATH ?= $(HOME_PATH)/.venv

PYTHON ?= PYTHONPATH=$(HOME_PATH) $(VENV_PATH)/bin/python
SYSTEM_PYTHON ?= python3

SRCFILES := ic tests

.PHONY: tea venv format lint clear demo

tea: venv format lint unittests demo

venv: ##
	test -d $(VENV_PATH) || $(SYSTEM_PYTHON) -m venv $(VENV_PATH) --clear
	$(PYTHON) -m pip install --requirement requirements.txt
	-$(PYTHON) -m pip install --requirement requirements-dev.txt

format:  ##
	$(PYTHON) -m black $(SRCFILES)
	$(PYTHON) -m isort --profile black $(SRCFILES)

lint:  ##
	$(PYTHON) -m black --check $(SRCFILES)
	$(PYTHON) -m ruff check $(SRCFILES)

unittests:  ##
	$(PYTHON) -m unittest discover --verbose --start-directory tests --pattern "test*.py"

clear:  ##
	rm -rvf $(SRCFILES)/**/*.pyc
	rm -rvf $(SRCFILES)/**/__pycache__

demo: DEMODIR := $(shell mktemp --directory --dry-run)
demo: XOR := $(shell head -c 256 /dev/urandom | md5sum --binary | cut -d' ' -f1)
demo:
	mkdir -pv "$(DEMODIR)"

	@echo "=== demodata"
	dd if=/dev/random of=$(DEMODIR)/demo.data bs=1048576 count=1
	@ls -l $(DEMODIR)/demo.data
	@md5sum --binary $(DEMODIR)/demo.data | cut -d' ' -f1 | tee $(DEMODIR)/demo.data.md5

	@echo "=== ic"
	$(PYTHON) -m ic $(DEMODIR)/demo.data $(DEMODIR)/demo.png
	@ls -lh $(DEMODIR)/demo.png
	-@identify $(DEMODIR)/demo.png

	$(PYTHON) -m ic -d $(DEMODIR)/demo.png $(DEMODIR)/demo-out.data
	@ls -l $(DEMODIR)/demo-out.data
	@md5sum --binary $(DEMODIR)/demo-out.data | grep `cat $(DEMODIR)/demo.data.md5`

	@echo "=== ic XOR"
	$(PYTHON) -m ic -x $(XOR) $(DEMODIR)/demo.data $(DEMODIR)/demo-xor.png
	@ls -lh $(DEMODIR)/demo-xor.png
	-@identify $(DEMODIR)/demo-xor.png

	$(PYTHON) -m ic -x $(XOR) -d $(DEMODIR)/demo-xor.png $(DEMODIR)/demo-xor-out.data
	@ls -l $(DEMODIR)/demo-xor-out.data
	@md5sum --binary $(DEMODIR)/demo-xor-out.data | grep `cat $(DEMODIR)/demo.data.md5`

	@echo "=== ic AUTOCROP"
	@convert $(DEMODIR)/demo.png -bordercolor Yellow -border 12x34 $(DEMODIR)/demo-pp.png
	-@identify $(DEMODIR)/demo-pp.png
	$(PYTHON) -m ic -d -a $(DEMODIR)/demo-pp.png $(DEMODIR)/demo-pp-out.data
	@ls -l $(DEMODIR)/demo-pp-out.data
	@md5sum --binary $(DEMODIR)/demo-pp-out.data | grep `cat $(DEMODIR)/demo.data.md5`

	@echo "=== ic SPLIT"
	$(PYTHON) -m ic -w 1024 -s 655360 $(DEMODIR)/demo.data
	@convert $(DEMODIR)/demo.data-000.png -bordercolor Red -border 12x34 $(DEMODIR)/demo.data-000-pp.png
	@convert $(DEMODIR)/demo.data-001.png -bordercolor Blue -border 56x78 $(DEMODIR)/demo.data-001-pp.png
	@ls -lh $(DEMODIR)/demo.data-00*.png
	$(PYTHON) -m ic -d -a $(DEMODIR)/demo.data-000-pp.png $(DEMODIR)/demo.data-000
	$(PYTHON) -m ic -d -a $(DEMODIR)/demo.data-001-pp.png $(DEMODIR)/demo.data-001
	@cat $(DEMODIR)/demo.data-000 $(DEMODIR)/demo.data-001 > $(DEMODIR)/demo.data-00x
	@md5sum --binary $(DEMODIR)/demo.data-00x | grep `cat $(DEMODIR)/demo.data.md5`

	@rm -rfv "$(DEMODIR)"
