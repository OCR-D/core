# OCR-D/core

> Python modules implementing [OCR-D specs](https://github.com/OCR-D/spec) and related tools

[![image](https://img.shields.io/pypi/v/ocrd.svg)](https://pypi.org/project/ocrd/)
[![Docker Image CI](https://github.com/OCR-D/core/actions/workflows/docker-image.yml/badge.svg)](https://github.com/OCR-D/core/actions/workflows/docker-image.yml)
[![Unit Test CI](https://github.com/OCR-D/core/actions/workflows/unit-test.yml/badge.svg)](https://github.com/OCR-D/core/actions/workflows/unit-test.yml)
[![image](https://codecov.io/gh/OCR-D/core/branch/master/graph/badge.svg)](https://codecov.io/gh/OCR-D/core)
[![image](https://scrutinizer-ci.com/g/OCR-D/core/badges/build.png?b=master)](https://scrutinizer-ci.com/g/OCR-D/core)
[![image](https://scrutinizer-ci.com/g/OCR-D/core/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/OCR-D/core)

[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/OCR-D/Lobby)


<!-- BEGIN-MARKDOWN-TOC -->
* [Introduction](#introduction)
* [Installation](#installation)
* [Command line tools](#command-line-tools)
	* [`ocrd` CLI](#ocrd-cli)
	* [`ocrd-dummy` CLI](#ocrd-dummy-cli)
* [Configuration](#configuration)
* [Packages](#packages)
	* [ocrd_utils](#ocrd_utils)
	* [ocrd_models](#ocrd_models)
	* [ocrd_modelfactory](#ocrd_modelfactory)
	* [ocrd_validators](#ocrd_validators)
	* [ocrd_network](#ocrd_network)
	* [ocrd](#ocrd)
* [bash library](#bash-library)
* [Testing](#testing)
* [See Also](#see-also)

<!-- END-MARKDOWN-TOC -->

## Introduction

This repository contains the python packages that form the base for tools within the
[OCR-D ecosphere](https://github.com/topics/ocr-d).

All packages are also published to [PyPI](https://pypi.org/search/?q=ocrd).

## Installation

**NOTE** Unless you want to contribute to OCR-D/core, we recommend installation
as part of [ocrd_all](https://github.com/OCR-D/ocrd_all) which installs a
complete stack of OCR-D-related software.

The easiest way to install is via `pip`:

    pip install ocrd


All Python software released by [OCR-D](https://github.com/OCR-D) requires Python 3.8 or higher.

> **NOTE** Some OCR-D tools (or even test cases) _might_ reveal an unintended behavior if you have specific environment modifications, like:
* using a custom build of [ImageMagick](https://github.com/ImageMagick/ImageMagick), whose format delegates are different from what OCR-D supposes
* custom Python logging configurations in your personal account

## Command line tools

**NOTE:** All OCR-D CLI tools support a `--help` flag which shows usage and
supported flags, options and arguments.

### `ocrd` CLI

* [CLI usage](https://ocr-d.de/core/api/ocrd/ocrd.cli.html)
* [Introduction to `ocrd workspace`](https://github.com/OCR-D/ocrd-website/wiki/Intro-ocrd-workspace-CLI)
* [OCR-D user guide](https://ocr-d.de/en/use)

### `ocrd-dummy` CLI

A minimal [OCR-D processor](https://ocr-d.de/en/user_guide#using-the-ocr-d-processors) that copies from `-I/-input-file-grp` to `-O/-output-file-grp`

## Configuration

Almost all behaviour of the OCR-D/core software is configured via CLI options and flags, which can be listed with the `--help` flag that all CLI support.

Some parts of the software are configured via environment variables:

* `OCRD_PROFILE`: This variable configures the built-in CPU and memory profiling. If empty, no profiling is done. Otherwise expected to contain any of the following tokens:
  * `CPU`: Enable CPU profiling of processor runs
  * `RSS`: Enable RSS memory profiling
  * `PSS`: Enable proportionate memory profiling
* `OCRD_PROFILE_FILE`: If set, then the CPU profile is written to this file for later peruse with a analysis tools like [snakeviz](https://jiffyclub.github.io/snakeviz/)

* `PATH`: Search path for processor executables (affects `ocrd process` and `ocrd resmgr`).
* `HOME`: Directory to look for `ocrd_logging.conf`, fallback for unset XDG variables (see below).

* `XDG_CONFIG_HOME`: Directory to look for `./ocrd/resources.yml` (i.e. `ocrd resmgr` user database) – defaults to `$HOME/.config`.
* `XDG_DATA_HOME`: Directory to look for `./ocrd-resources/*` (i.e. `ocrd resmgr` data location) – defaults to `$HOME/.local/share`.

* `OCRD_DOWNLOAD_RETRIES`: Number of times to retry failed attempts for downloads of resources or workspace files.
* `OCRD_DOWNLOAD_TIMEOUT`: Timeout in seconds for connecting or reading (comma-separated) when downloading.

* `OCRD_MISSING_INPUT`: How to deal with missing input files (for some fileGrp/pageId) during processing:
  * `SKIP`: ignore and proceed with next page's input
  * `ABORT`: throw `MissingInputFile` exception

* `OCRD_MISSING_OUTPUT`: How to deal with missing output files (for some fileGrp/pageId) during processing:
  * `SKIP`: ignore and proceed processing next page
  * `COPY`: fall back to copying input PAGE to output fileGrp for page
  * `ABORT`: re-throw whatever caused processing to fail

* `OCRD_MAX_MISSING_OUTPUTS`: Maximal rate of skipped/fallback pages among all processed pages before aborting (decimal fraction, ignored if negative).

* `OCRD_EXISTING_OUTPUT`: How to deal with already existing output files (for some fileGrp/pageId) during processing:
  * `SKIP`: ignore and proceed processing next page
  * `OVERWRITE`: force writing result to output fileGrp for page
  * `ABORT`: re-throw `FileExistsError` exception


* `OCRD_METS_CACHING`: Whether to enable in-memory storage of OcrdMets data structures for speedup during processing or workspace operations.

* `OCRD_MAX_PROCESSOR_CACHE`: Maximum number of processor instances (for each set of parameters) to be kept in memory (including loaded models) for processing workers or processor servers.

* `OCRD_MAX_PARALLEL_PAGES`: Maximum number of processor threads for page-parallel processing (within each Processor's selected page range, independent of the number of Processing Workers or Processor Servers). If set `>1`, then a METS Server must be used for METS synchronisation.

* `OCRD_PROCESSING_PAGE_TIMEOUT`: Timeout in seconds for processing a single page. If set >0, when exceeded, the same as OCRD_MISSING_OUTPUT applies.

* `OCRD_NETWORK_SERVER_ADDR_PROCESSING`: Default address of Processing Server to connect to (for `ocrd network client processing`).
* `OCRD_NETWORK_SERVER_ADDR_WORKFLOW`: Default address of Workflow Server to connect to (for `ocrd network client workflow`).
* `OCRD_NETWORK_SERVER_ADDR_WORKSPACE`: Default address of Workspace Server to connect to (for `ocrd network client workspace`).
* `OCRD_NETWORK_RABBITMQ_CLIENT_CONNECT_ATTEMPTS`: Number of attempts for a worker to create its queue. Helpful if the rabbitmq-server needs time to be fully started.

* `OCRD_NETWORK_CLIENT_POLLING_SLEEP`: How many seconds to sleep before trying `ocrd network client` again.
* `OCRD_NETWORK_CLIENT_POLLING_TIMEOUT`: Timeout for a blocking `ocrd network client` (in seconds).

* `OCRD_NETWORK_SOCKETS_ROOT_DIR`: The root directory where all mets server related socket files are created.
* `OCRD_NETWORK_LOGS_ROOT_DIR`: The root directory where all ocrd_network related file logs are stored.



## Packages

### ocrd_utils

Contains utilities and constants, e.g. for logging, path normalization, coordinate calculation etc.

See [README for `ocrd_utils`](./README_ocrd_utils.md) for further information.

### ocrd_models

Contains file format wrappers for PAGE-XML, METS, EXIF metadata etc.

See [README for `ocrd_models`](./README_ocrd_models.md) for further information.

### ocrd_modelfactory

Code to instantiate [models](#ocrd-models) from existing data.

See [README for `ocrd_modelfactory`](./README_ocrd_modelfactory.md) for further information.

### ocrd_validators

Schemas and routines for validating BagIt, `ocrd-tool.json`, workspaces, METS, page, CLI parameters etc.

See [README for `ocrd_validators`](./README_ocrd_validators.md) for further information.

### ocrd_network

Components related to OCR-D Web API

See [README for `ocrd_network`](./README_ocrd_network.md) for further information.

### ocrd

Depends on all of the above, also contains decorators and classes for creating OCR-D processors and CLIs.

Also contains the command line tool `ocrd`.

See [README for `ocrd`](./README_ocrd.md) for further information.

## bash library

Builds a bash script that can be sourced by other bash scripts to create OCRD-compliant CLI.

See [README for `bashlib`](./README_bashlib.md) for further information.

## Testing

Download assets (`make assets`)

Test with local files: `make test`

- Test with remote assets:
  - `make test OCRD_BASEURL='https://github.com/OCR-D/assets/raw/master/data/'`

## See Also

  - [OCR-D Specifications](https://https://ocr-d.de/en/spec/) ([Repo](https://github.com/ocr-d/spec))
  - [OCR-D core API documentation](https://ocr-d.de/core) (built here via `make docs`)
  - [OCR-D Website](https://ocr-d.de) ([Repo](https://github.com/ocr-d/ocrd-website))
