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

.PHONY: deps-cuda deps-ubuntu deps-test

deps-cuda: CONDA_EXE ?= /usr/local/bin/conda
deps-cuda: export CONDA_PREFIX ?= /conda
deps-cuda: PYTHON_PREFIX != $(PYTHON) -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])'
deps-cuda:
	curl --retry 6 -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest | tar -xvj bin/micromamba
	mv bin/micromamba $(CONDA_EXE)
# Install Conda system-wide (for interactive / login shells)
	echo 'export MAMBA_EXE=$(CONDA_EXE) MAMBA_ROOT_PREFIX=$(CONDA_PREFIX) CONDA_PREFIX=$(CONDA_PREFIX) PATH=$(CONDA_PREFIX)/bin:$$PATH' >> /etc/profile.d/98-conda.sh
# workaround for tf-keras#62
	echo 'export XLA_FLAGS=--xla_gpu_cuda_data_dir=$(CONDA_PREFIX)/' >> /etc/profile.d/98-conda.sh
	mkdir -p $(CONDA_PREFIX)/lib $(CONDA_PREFIX)/include
	echo $(CONDA_PREFIX)/lib >> /etc/ld.so.conf.d/conda.conf
# Get CUDA toolkit, including compiler and libraries with dev,
# however, the Nvidia channels do not provide (recent) cudnn (needed for Torch, TF etc):
#MAMBA_ROOT_PREFIX=$(CONDA_PREFIX) \
#conda install -c nvidia/label/cuda-11.8.0 cuda && conda clean -a
#
# The conda-forge channel has cudnn and cudatoolkit but no cudatoolkit-dev anymore (and we need both!),
# so let's combine nvidia and conda-forge (will be same lib versions, no waste of space),
# but omitting cuda-cudart-dev and cuda-libraries-dev (as these will be pulled by pip for torch anyway):
	MAMBA_ROOT_PREFIX=$(CONDA_PREFIX) \
	conda install -c nvidia/label/cuda-11.8.0 \
	                 cuda-nvcc \
	                 cuda-cccl \
	 && conda clean -a \
	 && find $(CONDA_PREFIX) -name "*_static.a" -delete
#conda install -c conda-forge \
#          cudatoolkit=11.8.0 \
#          cudnn=8.8.* && \
#conda clean -a && \
#find $(CONDA_PREFIX) -name "*_static.a" -delete
#
# Since Torch will pull in the CUDA libraries (as Python pkgs) anyway,
# let's jump the shark and pull these via NGC index directly,
# but then share them with the rest of the system so native compilation/linking
# works, too:
	shopt -s nullglob; \
	$(PIP) install nvidia-pyindex \
	 && $(PIP) install nvidia-cudnn-cu11==8.7.* \
	                   nvidia-cublas-cu11~=11.11 \
	                   nvidia-cusparse-cu11~=11.7 \
	                   nvidia-cusolver-cu11~=11.4 \
	                   nvidia-curand-cu11~=10.3 \
	                   nvidia-cufft-cu11~=10.9 \
	                   nvidia-cuda-runtime-cu11~=11.8 \
	                   nvidia-cuda-cupti-cu11~=11.8 \
	                   nvidia-cuda-nvrtc-cu11 \
	 && for pkg in cudnn cublas cusparse cusolver curand cufft cuda_runtime cuda_cupti cuda_nvrtc; do \
	        for lib in $(PYTHON_PREFIX)/nvidia/$$pkg/lib/lib*.so.*; do \
	            base=`basename $$lib`; \
	            ln -s $$lib $(CONDA_PREFIX)/lib/$$base.so; \
	            ln -s $$lib $(CONDA_PREFIX)/lib/$${base%.so.*}.so; \
	        done \
	     && for inc in $(PYTHON_PREFIX)/nvidia/$$pkg/include/*; do \
	            base=`basename $$inc`; case $$base in __*) continue; esac; \
	            ln -s $$inc $(CONDA_PREFIX)/include/; \
	        done \
	    done \
	 && ldconfig
# gputil/nvidia-smi would be nice, too – but that drags in Python as a conda dependency...

# Workaround for missing prebuilt versions of TF<2 for Python==3.8
# todo: find another solution for 3.9, 3.10 etc
# https://docs.nvidia.com/deeplearning/frameworks/tensorflow-wheel-release-notes/tf-wheel-rel.html
# Nvidia has them, but under a different name, so let's rewrite that:
# (hold at nv22.11, because newer releases require CUDA 12, which is not supported by TF2 (at py38),
#  and therefore not in our ocrd/core-cuda base image yet)
# However, at that time no Numpy 1.24 was known, which breaks TF1
# (which is why later nv versions hold it at <1.24 automatically -
#  see https://github.com/NVIDIA/tensorflow/blob/r1.15.5%2Bnv22.11/tensorflow/tools/pip_package/setup.py)
deps-tf1:
	if $(PYTHON) -c 'import sys; print("%u.%u" % (sys.version_info.major, sys.version_info.minor))' | fgrep 3.8 && \
	! $(PIP) show -q tensorflow-gpu; then \
	  $(PIP) install nvidia-pyindex && \
	  pushd $$(mktemp -d) && \
	  $(PIP) download --no-deps nvidia-tensorflow==1.15.5+nv22.11 && \
	  for name in nvidia_tensorflow-*.whl; do name=$${name%.whl}; done && \
	  $(PYTHON) -m wheel unpack $$name.whl && \
	  for name in nvidia_tensorflow-*/; do name=$${name%/}; done && \
	  newname=$${name/nvidia_tensorflow/tensorflow_gpu} &&\
	  sed -i s/nvidia_tensorflow/tensorflow_gpu/g $$name/$$name.dist-info/METADATA && \
	  sed -i s/nvidia_tensorflow/tensorflow_gpu/g $$name/$$name.dist-info/RECORD && \
	  sed -i s/nvidia_tensorflow/tensorflow_gpu/g $$name/tensorflow_core/tools/pip_package/setup.py && \
	  pushd $$name && for path in $$name*; do mv $$path $${path/$$name/$$newname}; done && popd && \
	  $(PYTHON) -m wheel pack $$name && \
	  $(PIP) install $$newname*.whl && popd && rm -fr $$OLDPWD; \
	  $(PIP) install "numpy<1.24"; \
	else \
	$(PIP) install "tensorflow-gpu<2.0"; \
	fi

deps-tf2:
	if $(PYTHON) -c 'import sys; print("%u.%u" % (sys.version_info.major, sys.version_info.minor))' | fgrep 3.8; then \
	$(PIP) install tensorflow; \
	else \
	$(PIP) install "tensorflow[and-cuda]"; \
	fi

deps-torch:
	$(PIP) install -i https://download.pytorch.org/whl/cu118 torch torchvision

# Dependencies for deployment in an ubuntu/debian linux
deps-ubuntu:
	apt-get install -y python3 imagemagick libgeos-dev libxml2-dev libxslt-dev libssl-dev

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
	# hack to prevent #451: enum keys will be strings
	sed -i 's/(Enum):$$/(str, Enum):/' $(GDS_PAGE)
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

network-module-test: assets
	$(PYTHON) \
		-m pytest $(PYTEST_ARGS) -k 'test_modules_' -s -v --durations=10\
		--ignore-glob="$(TESTDIR)/network/test_integration_*.py" \
		$(TESTDIR)/network

INTEGRATION_TEST_IN_DOCKER = docker exec core_test
network-integration-test:
	$(DOCKER_COMPOSE) --file tests/network/docker-compose.yml up -d
	-$(INTEGRATION_TEST_IN_DOCKER) pytest -k 'test_integration_' -v --ignore-glob="tests/network/*ocrd_all*.py"
	$(DOCKER_COMPOSE) --file tests/network/docker-compose.yml down --remove-orphans

network-integration-test-cicd:
	$(DOCKER_COMPOSE) --file tests/network/docker-compose.yml up -d
	$(INTEGRATION_TEST_IN_DOCKER) pytest -k 'test_integration_' -v --ignore-glob="tests/network/*ocrd_all*.py"
	$(DOCKER_COMPOSE) --file tests/network/docker-compose.yml down --remove-orphans

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
docker: DOCKER_BASE_IMAGE = ubuntu:20.04
docker: DOCKER_TAG = $(DOCKER_BASE_TAG:%=%/core)
docker: DOCKER_FILE = Dockerfile

# Build extended sets for maximal layer sharing
docker-cuda: DOCKER_BASE_IMAGE = $(DOCKER_BASE_TAG)/core
docker-cuda: DOCKER_TAG = $(DOCKER_BASE_TAG:%=%/core-cuda)
docker-cuda: DOCKER_FILE = Dockerfile.cuda

docker-cuda: docker

docker-cuda-tf1: DOCKER_BASE_IMAGE = $(DOCKER_BASE_TAG)/core-cuda
docker-cuda-tf1: DOCKER_TAG = $(DOCKER_BASE_TAG:%=%/core-cuda-tf1)
docker-cuda-tf1: DOCKER_FILE = Dockerfile.cuda-tf1

docker-cuda-tf1: docker-cuda

docker-cuda-tf2: DOCKER_BASE_IMAGE = $(DOCKER_BASE_TAG)/core-cuda
docker-cuda-tf2: DOCKER_TAG = $(DOCKER_BASE_TAG:%=%/core-cuda-tf2)
docker-cuda-tf2: DOCKER_FILE = Dockerfile.cuda-tf2

docker-cuda-tf2: docker-cuda

docker-cuda-torch: DOCKER_BASE_IMAGE = $(DOCKER_BASE_TAG)/core-cuda
docker-cuda-torch: DOCKER_TAG = $(DOCKER_BASE_TAG:%=%/core-cuda-torch)
docker-cuda-torch: DOCKER_FILE = Dockerfile.cuda-torch

docker-cuda-torch: docker-cuda

docker docker-cuda docker-cuda-tf1 docker-cuda-tf2 docker-cuda-torch:
	$(DOCKER_BUILD) -f $(DOCKER_FILE) $(DOCKER_TAG:%=-t %) --target ocrd_core_base --build-arg BASE_IMAGE=$(lastword $(DOCKER_BASE_IMAGE)) $(DOCKER_ARGS) .

# Build wheels and source dist and twine upload them
pypi: build
	twine upload --verbose dist/ocrd-$(VERSION)*{tar.gz,whl}
