export

SHELL = /bin/bash
PYTHON = python
PYTHONPATH := .:$(PYTHONPATH)
PIP = pip
LOG_LEVEL = INFO
PYTHONIOENCODING=utf8

# BEGIN-EVAL makefile-parser --make-help Makefile

help:
	@echo ""
	@echo "  Targets"
	@echo ""
	@echo "    deps-ubuntu    Dependencies for deployment in an ubuntu/debian linux"
	@echo "    deps-pip       Install python deps via pip"
	@echo "    assets         Clone the ocrd-assets repo for sample files"
	@echo "    install        (Re)install the tool"
	@echo "    test-deps-pip  Install test python deps via pip"
	@echo "    test           Run all unit tests"
	@echo "    docs           Build documentation"
	@echo "    docs-clean     Clean docs"

# END-EVAL

# Docker tag.
DOCKER_TAG = 'ocrd/pyocrd'

# Dependencies for deployment in an ubuntu/debian linux
deps-ubuntu:
	apt install -y \
		python3 \
		python3-pip \
		libtesseract-dev \
		libleptonica-dev \
		libimage-exiftool-perl \
		libxml2-utils \
		tesseract-ocr-eng

# Install python deps via pip
deps-pip:
	$(PIP) install -r requirements.txt

# Clone the ocrd-assets repo for sample files
assets:
	if [ ! -e ocrd-assets ];then git clone https://github.com/OCR-D/ocrd-assets;fi
	mkdir -p test/assets
	cp -r -t test/assets ocrd-assets/data/*
	# cd test/assets && ln -fs ../../ocrd-assets/data/* .

# Remove symlinks in test/assets
assets-clean:
	rm -rf test/assets

# (Re)install the tool
install:
	$(PIP) install .

#
# Tests
#

test/assets: spec
	mkdir -p test/assets
	cp -r spec/io/example test/assets/herold

# Install test python deps via pip
test-deps-pip:
	$(PIP) install -r requirements_test.txt

.PHONY: test
# Run all unit tests
test:
	$(PYTHON) -m pytest --duration=10 test

#
# Documentation
#

.PHONY: docs
# Build documentation
docs: gh-pages
	sphinx-apidoc -f -o docs/api ocrd
	cd docs ; $(MAKE) html
	cp -r docs/build/html/* gh-pages
	cd gh-pages; git add . && git commit -m 'Updated docs $$(date)' && git push

# Clean docs
docs-clean:
	cd docs ; rm -rf _build api

gh-pages:
	git clone --branch gh-pages https://github.com/OCR-D/pyocrd gh-pages

#
# Clean up
#

pyclean:
	rm -f **/*.pyc
	rm -rf **/*/__pycache__
	rm -rf .pytest_cache

test-profile:
	$(PYTHON) -m cProfile -o profile $$(which pytest)
	$(PYTHON) analyze_profile.py

# Start asset server at http://localhost:5001
asset-server:
	cd ocrd-assets && make start

#
# Docker
#

# Build docker image
docker:
	docker build -t $(DOCKER_TAG) .
