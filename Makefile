export

SHELL = /bin/bash
PYTHON = python
PIP = pip
LOG_LEVEL = INFO
PYTHONIOENCODING=utf8
TESTDIR = tests

# PAGE schema version to use. Default: '$(PAGE_VERSION)'
PAGE_VERSION = 2019

SPHINX_APIDOC = 

BUILD_ORDER = ocrd_utils ocrd_models ocrd_modelfactory ocrd_validators ocrd

FIND_VERSION = grep version= ocrd_utils/setup.py|grep -Po "([0-9ab]+\.?)+"

# Additional arguments to docker build. Default: '$(DOCKER_ARGS)'
DOCKER_ARGS = 

# BEGIN-EVAL makefile-parser --make-help Makefile

help:
	@echo ""
	@echo "  Targets"
	@echo ""
	@echo "    deps-ubuntu    Dependencies for deployment in an ubuntu/debian linux"
	@echo "    deps-test      Install test python deps via pip"
	@echo "    install        (Re)install the tool"
	@echo "    uninstall      Uninstall the tool"
	@echo "    generate-page  Regenerate python code from PAGE XSD"
	@echo "    repo/assets    Clone OCR-D/assets to ./repo/assets"
	@echo "    repo/spec      Clone OCR-D/spec to ./repo/spec"
	@echo "    spec           Copy JSON Schema, OpenAPI from OCR-D/spec"
	@echo "    assets         Setup test assets"
	@echo "    assets-server  Start asset server at http://localhost:5001"
	@echo "    assets-clean   Remove symlinks in $(TESTDIR)/assets"
	@echo "    test           Run all unit tests"
	@echo "    docs           Build documentation"
	@echo "    docs-clean     Clean docs"
	@echo "    docs-coverage  Calculate docstring coverage"
	@echo "    docker         Build docker image"
	@echo "    bashlib        Build bash library"
	@echo "    pypi           Build wheels and source dist and twine upload them"
	@echo ""
	@echo "  Variables"
	@echo ""
	@echo "    PAGE_VERSION  PAGE schema version to use. Default: '$(PAGE_VERSION)'"
	@echo "    DOCKER_ARGS   Additional arguments to docker build. Default: '$(DOCKER_ARGS)'"
	@echo "    DOCKER_TAG    Docker tag."
	@echo "    PIP_INSTALL   pip install command. Default: $(PIP_INSTALL)"

# END-EVAL

# Docker tag.
DOCKER_TAG = 'ocrd/core'

# pip install command. Default: $(PIP_INSTALL)
PIP_INSTALL = pip install

# Dependencies for deployment in an ubuntu/debian linux
deps-ubuntu:
	apt-get install -y python3 python3-pip python3-venv

# Install test python deps via pip
deps-test:
	$(PIP) install -r requirements_test.txt

# (Re)install the tool
install: spec
	$(PIP) install -U "pip>=19.0.0" wheel
	for mod in $(BUILD_ORDER);do (cd $$mod ; $(PIP_INSTALL) .);done

# Uninstall the tool
uninstall:
	for mod in $(BUILD_ORDER);do pip uninstall -y $$mod;done

# Regenerate python code from PAGE XSD
generate-page: repo/assets
	generateDS \
		-f \
		--root-element='PcGts' \
		-o ocrd_models/ocrd_models/ocrd_page_generateds.py \
		repo/assets/data/schema/data/$(PAGE_VERSION).xsd

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
	cp repo/spec/ocrd_tool.schema.yml ocrd_validators/ocrd_validators/ocrd_tool.schema.yml
	cp repo/spec/bagit-profile.yml ocrd_validators/ocrd_validators/bagit-profile.yml

#
# Assets
#

# Setup test assets
assets: repo/assets
	mkdir -p $(TESTDIR)/assets
	cp -r -t $(TESTDIR)/assets repo/assets/data/*

# Start asset server at http://localhost:5001
assets-server:
	cd assets && make start

# Remove symlinks in $(TESTDIR)/assets
assets-clean:
	rm -rf $(TESTDIR)/assets

#
# Tests
#

.PHONY: test
# Run all unit tests
test: spec assets
	HOME=$(CURDIR)/ocrd_utils $(PYTHON) -m pytest --continue-on-collection-errors $(TESTDIR) -k TestLogging
	HOME=$(CURDIR) $(PYTHON) -m pytest --continue-on-collection-errors $(TESTDIR)

test-profile:
	$(PYTHON) -m cProfile -o profile $$(which pytest)
	$(PYTHON) analyze_profile.py

coverage: assets-clean assets
	coverage erase
	make test PYTHON="coverage run"
	coverage report
	coverage html

#
# Documentation
#

.PHONY: docs
# Build documentation
docs:
	for mod in $(BUILD_ORDER);do sphinx-apidoc -f -M -e -o docs/api/$$mod $$mod/$$mod 'ocrd_models/ocrd_models/ocrd_page_generateds.py';done
	cd docs ; $(MAKE) html

docs-push: gh-pages docs
	cp -r docs/build/html/* gh-pages
	cd gh-pages; git add . && git commit -m 'Updated docs $$(date)' && git push

# Clean docs
docs-clean:
	cd gh-pages ; rm -rf *
	cd docs ; rm -rf _build api/ocrd api/ocrd_*

# Calculate docstring coverage
docs-coverage:
	for mod in $(BUILD_ORDER);do docstr-coverage $$mod/$$mod -e '.*(ocrd_page_generateds|/ocrd/cli/).*';done
	for mod in $(BUILD_ORDER);do echo "# $$mod"; docstr-coverage -v1 $$mod/$$mod -e '.*(ocrd_page_generateds|/ocrd/cli/).*'|sed 's/^/\t/';done

gh-pages:
	git clone --branch gh-pages https://github.com/OCR-D/core gh-pages

#
# Clean up
#

pyclean:
	rm -f **/*.pyc
	find . -name '__pycache__' -exec rm -rf '{}' \;
	rm -rf .pytest_cache

#
# Docker
#

# Build docker image
docker:
	docker build -t $(DOCKER_TAG) $(DOCKER_ARGS) .

#
# bash library
#
.PHONY: bashlib

# Build bash library
bashlib:
	cd ocrd/bashlib; make lib

# Build wheels and source dist and twine upload them
pypi: uninstall install
	for mod in $(BUILD_ORDER);do (cd $$mod; $(PYTHON) setup.py sdist bdist_wheel);done
	version=`$(FIND_VERSION)`; twine upload ocrd*/dist/ocrd*$$version*{tar.gz,whl}
