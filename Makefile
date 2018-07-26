export

SHELL = /bin/bash
PYTHON = python
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
	@echo "    deps-pip-test  Install test python deps via pip"
	@echo "    install        (Re)install the tool"
	@echo "    repo/assets    Clone OCR-D/assets to ./repo/assets"
	@echo "    repo/spec      Clone OCR-D/spec to ./repo/spec"
	@echo "    spec           Copy JSON Schema, OpenAPI from OCR-D/spec"
	@echo "    assets         Setup test assets"
	@echo "    assets-server  Start asset server at http://localhost:5001"
	@echo "    assets-clean   Remove symlinks in test/assets"
	@echo "    test           Run all unit tests"
	@echo "    docs           Build documentation"
	@echo "    docs-clean     Clean docs"
	@echo "    docker         Build docker image"
	@echo ""
	@echo "  Variables"
	@echo ""
	@echo "    DOCKER_TAG  Docker tag."

# END-EVAL

# Docker tag.
DOCKER_TAG = 'ocrd/pyocrd'

# Dependencies for deployment in an ubuntu/debian linux
deps-ubuntu:
	sudo apt install -y \
		python3 \
		python3-pip \
		libimage-exiftool-perl

# Install python deps via pip
deps-pip:
	$(PIP) install -r requirements.txt

# Install test python deps via pip
deps-pip-test:
	$(PIP) install -r requirements_test.txt

# (Re)install the tool
install: spec
	$(PIP) install .

# Regenerate python code from PAGE XSD
generate-page: repo/assets
	generateDS \
		-f \
		--no-namespace-defs \
		--root-element='PcGts' \
		-o ocrd/model/ocrd_page_generateds.py \
		repo/assets/data/schema/2018.xsd

#
# Repos
#

# Clone OCR-D/assets to ./repo/assets
repo/assets:
	mkdir -p $(dir $@)
	git clone https://github.com/OCR-D/assets "$@"

# Clone OCR-D/spec to ./repo/spec
repo/spec:
	mkdir -p $(dir $@)
	git clone https://github.com/OCR-D/spec "$@"

#
# Spec
#

.PHONY: spec
# Copy JSON Schema, OpenAPI from OCR-D/spec
spec: repo/spec
	cp repo/spec/ocrd_api.swagger.yml ocrd/model/yaml/ocrd_oas3.spec.yml
	cp repo/spec/ocrd_tool.schema.yml ocrd/model/yaml/ocrd_tool.schema.yml

#
# Assets
#

# Setup test assets
assets: repo/assets
	mkdir -p test/assets
	cp -r -t test/assets repo/assets/data/*

# Start asset server at http://localhost:5001
assets-server:
	cd assets && make start

# Remove symlinks in test/assets
assets-clean:
	rm -rf test/assets

#
# Tests
#

.PHONY: test
# Run all unit tests
test: spec
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
	find ocrd -name '__pycache__' -exec rm -rf '{}' \;
	rm -rf .pytest_cache

test-profile:
	$(PYTHON) -m cProfile -o profile $$(which pytest)
	$(PYTHON) analyze_profile.py

#
# Docker
#

# Build docker image
docker:
	docker build -t $(DOCKER_TAG) .

#
# bash library
#
.PHONY: bashlib

# Build bash library
bashlib:
	cd bashlib; make lib
