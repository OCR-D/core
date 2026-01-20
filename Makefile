export

SHELL = /bin/bash
PYTHON ?= python
PIP ?= pip
LOG_LEVEL = INFO
PYTHONIOENCODING=utf8
TESTDIR = $(CURDIR)/tests
PYTEST_ARGS = --continue-on-collection-errors
VERSION = $(shell cat VERSION)

DOCKER_COMPOSE = docker compose

SPHINX_APIDOC =

BUILD_ORDER = ocrd_utils ocrd_models ocrd_modelfactory ocrd_validators ocrd_network ocrd
reverse = $(if $(wordlist 2,2,$(1)),$(call reverse,$(wordlist 2,$(words $(1)),$(1))) $(firstword $(1)),$(1))

# BEGIN-EVAL makefile-parser --make-help Makefile

help:
	@echo ""
	@echo "  Targets"
	@echo ""
	@echo "    deps-cuda      Dependencies for deployment with GPU support via Conda"
	@echo "    deps-ubuntu    Dependencies for deployment in an Ubuntu/Debian Linux"
	@echo "    deps-test      Install test python deps via pip"
	@echo "    build          (Re)build source and binary distributions of pkges"
	@echo "    install        (Re)install the packages"
	@echo "    install-dev    Install with pip install -e"
	@echo "    uninstall      Uninstall the packages"
	@echo "    generate-page  Regenerate python code from PAGE XSD"
	@echo "    spec           Copy JSON Schema, OpenAPI from OCR-D/spec"
	@echo "    assets         Setup test assets"
	@echo "    test           Run all unit tests"
	@echo "    docs           Build documentation"
	@echo "    docs-clean     Clean docs"
	@echo "    docs-coverage  Calculate docstring coverage"
	@echo "    docker         Build docker image"
	@echo "    docker-cuda    Build docker image for GPU / CUDA"
	@echo "    pypi           Build wheels and source dist and twine upload them"
	@echo " ocrd network tests"
	@echo "    network-module-test       Run all ocrd_network module tests"
	@echo "    network-integration-test  Run all ocrd_network integration tests (docker and docker compose required)"
	@echo ""
	@echo "  Variables"
	@echo ""
	@echo "    DOCKER_TAG         Docker target image tag. Default: '$(DOCKER_TAG)'."
	@echo "    DOCKER_BASE_IMAGE  Docker source image tag. Default: '$(DOCKER_BASE_IMAGE)'."
	@echo "    DOCKER_ARGS        Additional arguments to docker build. Default: '$(DOCKER_ARGS)'"
	@echo "    PIP_INSTALL        pip install command. Default: $(PIP_INSTALL)"
	@echo "    PYTEST_ARGS        arguments for pytest. Default: $(PYTEST_ARGS)"

# END-EVAL

# pip install command. Default: $(PIP_INSTALL)
PIP_INSTALL ?= $(PIP) install
PIP_INSTALL_CONFIG_OPTION ?=

.PHONY: get-conda deps-cuda deps-ubuntu deps-test

ifeq ($(shell command -v conda),)
# Conda installation: get Micromamba distribution
get-conda: CONDA_EXE ?= /usr/local/bin/conda
get-conda: export CONDA_PREFIX ?= /conda
# first part of recipe: see micro.mamba.pm/install.sh
get-conda: OS != uname
get-conda: PLATFORM = $(subst Darwin,osx,$(subst Linux,linux,$(OS)))
get-conda: ARCH != uname -m
get-conda: MACHINE = $(or $(filter aarch64 ppc64le, $(subst arm64,aarch64,$(ARCH))), 64)
get-conda: URL = https://micro.mamba.pm/api/micromamba/$(PLATFORM)-$(MACHINE)/latest
get-conda:
	curl --retry 6 -Ls $(URL) | tar -xvj bin/micromamba
	mv bin/micromamba $(CONDA_EXE)
# Install Conda system-wide (for interactive / login shells)
	echo 'export MAMBA_EXE=$(CONDA_EXE) MAMBA_ROOT_PREFIX=$(CONDA_PREFIX) CONDA_PREFIX=$(CONDA_PREFIX) PATH=$(CONDA_PREFIX)/bin:$$PATH' >> /etc/profile.d/98-conda.sh
# workaround for tf-keras#62
	echo 'export XLA_FLAGS=--xla_gpu_cuda_data_dir=$(CONDA_PREFIX)/' >> /etc/profile.d/98-conda.sh
	mkdir -p $(CONDA_PREFIX)/lib $(CONDA_PREFIX)/include
	echo $(CONDA_PREFIX)/lib >> /etc/ld.so.conf.d/conda.conf
else
# Conda installation already present: do nothing
get-conda: ;
endif

# Dependencies for CUDA installation via Conda
deps-cuda: PYTHON_PREFIX != $(PYTHON) -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'
deps-cuda: get-conda
# Get CUDA toolkit, including compiler and libraries with dev from NVIDIA channels
# Get CUDNN (needed for Torch, TF etc) from conda-forge.
# CUDA runtime libs will be pulled by `pip` for TF and Torch differently anyway,
# so do _not_ install them here to avoid wasting space.
	conda install -c nvidia/label/cuda-12.4.0 cuda-minimal-build \
	&& conda clean -a && ldconfig

deps-tf2:
	$(PIP) install "tensorflow[and-cuda]"  -r requirements.txt

deps-torch:
	$(PIP) install torch==2.5.1 torchvision==0.20.1 --extra-index-url https://download.pytorch.org/whl/cu124 -r requirements.txt

# deps-*: always mix core's requirements.txt with additional deps,
# so pip does not ignore the older version reqs,
# but instead tries to find a mutually compatible set.

# Dependencies for deployment in an ubuntu/debian linux
deps-ubuntu:
	apt-get update
	apt-get install -y bzip2 python3 imagemagick libgeos-dev libxml2-dev libxslt-dev libssl-dev

# Dependencies for deployment via Conda
deps-conda: get-conda
	conda install -c conda-forge python==3.10.* imagemagick geos pkgconfig

# Install test python deps via pip
deps-test:
	$(PIP) install -U pip
	$(PIP) install -r requirements_test.txt

.PHONY: build install install-dev uninstall

build:
	$(PIP) install build
	$(PYTHON) -m build .
# or use -n ?

# (Re)install the tool
install: #build
	# not strictly necessary but a precaution against outdated python build tools, https://github.com/OCR-D/core/pull/1166
	$(PIP) install -U pip wheel
	$(PIP_INSTALL) . $(PIP_INSTALL_CONFIG_OPTION)
	@# workaround for shapely#1598
	$(PIP) config set global.no-binary shapely

# Install with pip install -e
install-dev: PIP_INSTALL = $(PIP) install -e
install-dev: PIP_INSTALL_CONFIG_OPTION = --config-settings editable_mode=strict
install-dev: uninstall
	$(MAKE) install

# Uninstall the tool
uninstall:
	$(PIP) uninstall --yes ocrd

# Regenerate python code from PAGE XSD
generate-page: GDS_PAGE = src/ocrd_models/ocrd_page_generateds.py
generate-page: GDS_PAGE_USER = src/ocrd_page_user_methods.py
generate-page: repo/assets
	generateDS \
		-f \
		--root-element='PcGts' \
		-o $(GDS_PAGE) \
		--silence \
		--export "write etree" \
		--disable-generatedssuper-lookup \
		--user-methods=$(GDS_PAGE_USER) \
		src/ocrd_validators/page.xsd
	# hack to ensure output has pc: prefix
	@#sed -i "s/namespaceprefix_=''/namespaceprefix_='pc:'/" $(GDS_PAGE)
	sed -i 's/_nsprefix_ = None/_nsprefix_ = "pc"/' $(GDS_PAGE)
	# hack to ensure child nodes also have pc: prefix...
	sed -i 's/.*_nsprefix_ = child_.prefix$$//' $(GDS_PAGE)
	# replace the need for six since we target python 3.6+
	sed -i 's/from six.moves/from itertools/' $(GDS_PAGE)

#
# Repos
#
.PHONY: repos always-update
repos: repo/assets repo/spec


# Update OCR-D/assets and OCR-D/spec resp.
repo/assets repo/spec: always-update
	git submodule sync --recursive $@
	if git submodule status --recursive $@ | grep -qv '^ '; then \
		git submodule update --init --recursive $@ && \
		touch $@; \
	fi

#
# Spec
#

.PHONY: spec
# Copy JSON Schema, OpenAPI from OCR-D/spec
spec: # repo/spec
	cp repo/spec/ocrd_tool.schema.yml src/ocrd_validators/ocrd_tool.schema.yml
	cp repo/spec/bagit-profile.yml src/ocrd_validators/bagit-profile.yml

#
# Assets
#

# Setup test assets
assets: repo/assets
	rm -rf $(TESTDIR)/assets
	mkdir -p $(TESTDIR)/assets
	cp -r repo/assets/data/* $(TESTDIR)/assets


#
# Tests
#

.PHONY: test
# Run all unit tests
test: assets
	$(PYTHON) \
		-m pytest $(PYTEST_ARGS) --durations=10\
		--ignore-glob="$(TESTDIR)/**/*bench*.py" \
		--ignore-glob="$(TESTDIR)/network/*.py" \
		$(TESTDIR)
	$(MAKE) test-logging

test-logging: assets
	# copy default logging to temporary directory and run logging tests from there
	tempdir=$$(mktemp -d); \
	cp src/ocrd_utils/ocrd_logging.conf $$tempdir; \
	cd $$tempdir; \
	$(PYTHON) -m pytest --continue-on-collection-errors -k TestLogging -k TestDecorators $(TESTDIR); \
	rm -r $$tempdir/ocrd_logging.conf $$tempdir/ocrd.log $$tempdir/.benchmarks; \
	rm -rf $$tempdir/.coverage; \
	rmdir $$tempdir

# ensure shapely#1598 does not hit
# ensure CUDA works for Torch or TF
test-cuda-torch:
	$(PYTHON) -c "from shapely.geometry import Polygon; import torch; torch.randn(10).cuda()"
	$(PYTHON) -c "import torch, sys; sys.exit(0 if torch.cuda.is_available() else 1)"
test-cuda-tf2 test-cuda-tf1:
	$(PYTHON) -c "import tensorflow as tf, sys; sys.exit(0 if tf.test.is_gpu_available() else 1)"

network-module-test: assets
	$(PYTHON) \
		-m pytest $(PYTEST_ARGS) -k 'test_modules_' -s -v --durations=10\
		--ignore-glob="$(TESTDIR)/network/test_integration_*.py" \
		$(TESTDIR)/network

network-integration-test: INTEGRATION_TEST_COMPOSE = $(DOCKER_COMPOSE) --file tests/network/docker-compose.yml
network-integration-test: INTEGRATION_TEST_IN_DOCKER = docker exec core_test
# do not attempt to update assets submodule during docker (compose) build,
# but copy the assets from the build context instead:
network-integration-test: export SKIP_ASSETS = 1
network-integration-test: assets
	{ $(INTEGRATION_TEST_COMPOSE) up --wait --wait-timeout 60 -d && \
	$(INTEGRATION_TEST_IN_DOCKER) pytest -s -k 'test_integration_' -v --ignore-glob="tests/network/*ocrd_all*.py" && \
	err=0 || { err=$$?; $(INTEGRATION_TEST_COMPOSE) logs; }; \
	$(INTEGRATION_TEST_COMPOSE) down --remove-orphans; exit $$err; }

benchmark:
	$(PYTHON) -m pytest $(TESTDIR)/model/test_ocrd_mets_bench.py

benchmark-extreme:
	$(PYTHON) -m pytest $(TESTDIR)/model/*bench*.py

test-profile:
	$(PYTHON) -m cProfile -o profile $$(which pytest)
	$(PYTHON) analyze_profile.py

coverage: assets
	coverage erase
	make test PYTHON="coverage run --omit='*generate*'"
	coverage report
	coverage html

#
# Documentation
#

.PHONY: docs
# Build documentation
docs:
	for mod in $(BUILD_ORDER);do sphinx-apidoc -f -M -e \
		-o docs/api/$$mod src/$$mod \
		'src/ocrd_models/ocrd_page_generateds.py' \
		;done
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
	rm -rf ./build
	rm -rf ./dist
	rm -rf htmlcov
	rm -rf .benchmarks
	rm -rf **/*.egg-info
	rm -f **/*.pyc
	-find . -name '__pycache__' -exec rm -rf '{}' \;
	rm -rf .pytest_cache

#
# Docker
#

.PHONY: docker docker-cuda

# Additional arguments to docker build. Default: '$(DOCKER_ARGS)'
DOCKER_ARGS ?=
DOCKER_BASE_TAG ?= ocrd
DOCKER_BUILD ?= docker build --progress=plain

# Build docker image
docker: DOCKER_BASE_IMAGE = ubuntu:22.04
docker: DOCKER_TAG = $(DOCKER_BASE_TAG:%=%/core)
docker: DOCKER_FILE = Dockerfile

# Build extended sets for maximal layer sharing
docker-cuda: DOCKER_BASE_IMAGE = $(DOCKER_BASE_TAG)/core
docker-cuda: DOCKER_TAG = $(DOCKER_BASE_TAG:%=%/core-cuda)
docker-cuda: DOCKER_FILE = Dockerfile.cuda

docker-cuda: docker

docker-cuda-tf2: DOCKER_BASE_IMAGE = $(DOCKER_BASE_TAG)/core-cuda
docker-cuda-tf2: DOCKER_TAG = $(DOCKER_BASE_TAG:%=%/core-cuda-tf2)
docker-cuda-tf2: DOCKER_FILE = Dockerfile.cuda-tf2

docker-cuda-tf2: docker-cuda

docker-cuda-torch: DOCKER_BASE_IMAGE = $(DOCKER_BASE_TAG)/core-cuda
docker-cuda-torch: DOCKER_TAG = $(DOCKER_BASE_TAG:%=%/core-cuda-torch)
docker-cuda-torch: DOCKER_FILE = Dockerfile.cuda-torch

docker-cuda-torch: docker-cuda

# if the current ref is a release, then use it as tag instead of :latest
docker docker-cuda docker-cuda-tf2 docker-cuda-torch: GIT_TAG := $(strip $(shell git describe --tags | grep -x "v[0-9]\.[0-9][[0-9]\.[0-9]"))
docker docker-cuda docker-cuda-tf2 docker-cuda-torch:
	$(DOCKER_BUILD) -f $(DOCKER_FILE) $(DOCKER_TAG:%=-t %) \
	$(if $(GIT_TAG),$(DOCKER_TAG:%=-t %:$(GIT_TAG))) \
	--target ocrd_core_base \
	--build-arg BASE_IMAGE=$(lastword $(DOCKER_BASE_IMAGE)) \
	--build-arg VCS_REF=$$(git rev-parse --short HEAD) \
	--build-arg BUILD_DATE=$$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
	$(DOCKER_ARGS) .

# Build wheels and source dist and twine upload them
pypi: build
	twine upload --verbose dist/ocrd-$(VERSION)*{tar.gz,whl}
