# OCR-D/core

> Python modules implementing [OCR-D specs](https://github.com/OCR-D/spec) and related tools

[![image](https://img.shields.io/pypi/v/ocrd.svg)](https://pypi.org/project/ocrd/)
[![image](https://travis-ci.org/OCR-D/core.svg?branch=master)](https://travis-ci.org/OCR-D/core)
[![image](https://circleci.com/gh/OCR-D/core.svg?style=svg)](https://circleci.com/gh/OCR-D/core)
[![image](https://scrutinizer-ci.com/g/OCR-D/core/badges/build.png?b=master)](https://scrutinizer-ci.com/g/OCR-D/core)
[![Docker Automated build](https://img.shields.io/docker/automated/ocrd/core.svg)](https://hub.docker.com/r/ocrd/core/tags/)
[![image](https://codecov.io/gh/OCR-D/core/branch/master/graph/badge.svg)](https://codecov.io/gh/OCR-D/core)
[![image](https://scrutinizer-ci.com/g/OCR-D/core/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/OCR-D/core)

[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/OCR-D/Lobby)


<!-- BEGIN-MARKDOWN-TOC -->
* [Introduction](#introduction)
* [Installation](#installation)
* [Command line tools](#command-line-tools)
	* [`ocrd` CLI](#ocrd-cli)
	* [`ocrd-dummy` CLI](#ocrd-dummy-cli)
* [Packages](#packages)
	* [ocrd_utils](#ocrd_utils)
	* [ocrd_models](#ocrd_models)
	* [ocrd_modelfactory](#ocrd_modelfactory)
	* [ocrd_validators](#ocrd_validators)
	* [ocrd](#ocrd)
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

```sh
pip install ocrd

# or just the functionality you need, e.g.

pip install ocrd_modelfactory
```

All python software released by [OCR-D](https://github.com/OCR-D) requires Python 3.6 or higher.

## Command line tools

**NOTE:** All OCR-D CLI tools support a `--help` flag which shows usage and
supported flags, options and arguments.

### `ocrd` CLI

* [OCR-D user guide](https://ocr-d.de/en/use)
* [Introduction to `ocrd workspace`](https://github.com/OCR-D/ocrd-website/wiki/Intro-ocrd-workspace-CLI)

### `ocrd-dummy` CLI

A minimal [OCR-D processor](https://ocr-d.de/en/user_guide#using-the-ocr-d-processors) that copies from `-I/-input-file-grp` to `-O/-output-file-grp`

## Packages

### ocrd_utils

Contains utilities and constants, e.g. for logging, path normalization, coordinate calculation etc.

See [README for `ocrd_utils`](./ocrd_utils/README.md) for further information.

### ocrd_models

Contains file format wrappers for PAGE-XML, METS, EXIF metadata etc.

See [README for `ocrd_models`](./ocrd_models/README.md) for further information.

### ocrd_modelfactory

Code to instantiate [models](#ocrd-models) from existing data.

See [README for `ocrd_modelfactory`](./ocrd_modelfactory/README.md) for further information.

### ocrd_validators

Schemas and routines for validating BagIt, `ocrd-tool.json`, workspaces, METS, page, CLI parameters etc.

See [README for `ocrd_validators`](./ocrd_validators/README.md) for further information.

### ocrd

Depends on all of the above, also contains decorators and classes for creating OCR-D processors and CLIs.

Also contains the command line tool `ocrd`.

See [README for `ocrd`](./ocrd/README.md) for further information.

## Testing

Download assets (`make assets`)

Test with local files: `make test`

- Test with local asset server:
  - Start asset-server: `make asset-server`
  - `make test OCRD_BASEURL='http://localhost:5001/'`

- Test with remote assets:
  - `make test OCRD_BASEURL='https://github.com/OCR-D/assets/raw/master/data/'`

## See Also

  - [OCR-D Specifications](https://https://ocr-d.de/en/spec/) ([Repo](https://github.com/ocr-d/spec))
  - [OCR-D core API documentation](https://ocr-d.de/core) (built here via `make docs`)
  - [OCR-D Website](https://ocr-d.de) ([Repo](https://github.com/ocr-d/ocrd-website))
