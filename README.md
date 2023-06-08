# OCR-D/core

> Python modules implementing [OCR-D specs](https://github.com/OCR-D/spec) and related tools

[![image](https://img.shields.io/pypi/v/ocrd.svg)](https://pypi.org/project/ocrd/)
[![image](https://circleci.com/gh/OCR-D/core.svg?style=svg)](https://circleci.com/gh/OCR-D/core)
[![Docker Image CI](https://github.com/OCR-D/core/actions/workflows/docker-image.yml/badge.svg)](https://github.com/OCR-D/core/actions/workflows/docker-image.yml)
[![image](https://scrutinizer-ci.com/g/OCR-D/core/badges/build.png?b=master)](https://scrutinizer-ci.com/g/OCR-D/core)
[![image](https://codecov.io/gh/OCR-D/core/branch/master/graph/badge.svg)](https://codecov.io/gh/OCR-D/core)
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
	* [bashlib API](#bashlib-api)
	* [`ocrd__raise`](#ocrd__raise)
	* [`ocrd__log`](#ocrd__log)
	* [`ocrd__minversion`](#ocrd__minversion)
	* [`ocrd__dumpjson`](#ocrd__dumpjson)
	* [`ocrd__usage`](#ocrd__usage)
	* [`ocrd__parse_argv`](#ocrd__parse_argv)
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

All python software released by [OCR-D](https://github.com/OCR-D) requires Python 3.7 or higher.

**NOTE** Some OCR-D-Tools (or even test cases) _might_ reveal an unintended behavior if you have specific environment modifications, like:
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

Some parts of the software are configured via environement variables:

* `OCRD_METS_CACHING`: If set to `true`, access to the METS file is cached, speeding in-memory search and modification.
* `OCRD_PROFILE`: This variable configures the built-in CPU and memory profiling. If empty, no profiling is done. Otherwise expected to contain any of the following tokens:
  * `CPU`: Enable CPU profiling of processor runs
  * `RSS`: Enable RSS memory profiling
  * `PSS`: Enable proportionate memory profiling
* `OCRD_PROFILE_FILE`: If set, then the CPU profile is written to this file for later peruse with a analysis tools like [snakeviz](https://jiffyclub.github.io/snakeviz/)

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

### ocrd_network

Components related to OCR-D Web API

See [README for `ocrd_network`](./ocrd_network/README.md) for further information.

### ocrd

Depends on all of the above, also contains decorators and classes for creating OCR-D processors and CLIs.

Also contains the command line tool `ocrd`.

See [README for `ocrd`](./ocrd/README.md) for further information.

## bash library

Builds a bash script that can be sourced by other bash scripts to create OCRD-compliant CLI.

For example:

    source `ocrd bashlib filename`
    declare -A NAMESPACES MIMETYPES
    eval NAMESPACES=( `ocrd bashlib constants NAMESPACES` )
    echo ${NAMESPACES[page]}
    eval MIMETYPE_PAGE=( `ocrd bashlib constants MIMETYPE_PAGE` )
    echo $MIMETYPE_PAGE
    eval MIMETYPES=( `ocrd bashlib constants EXT_TO_MIME` )
    echo ${MIMETYPES[.jpg]}


### bashlib CLI

See [CLI usage](https://ocr-d.de/core/api/ocrd/ocrd.cli.bashlib.html)

### bashlib API

### `ocrd__raise`

Raise an error and exit.

### `ocrd__log`

Delegate logging to [`ocrd log`](#ocrd-cli)

### `ocrd__minversion`

Ensure minimum version

### `ocrd__dumpjson`

Output ocrd-tool.json content verbatim.

Requires `$OCRD_TOOL_JSON` and `$OCRD_TOOL_NAME` to be set:

```sh
export OCRD_TOOL_JSON=/path/to/ocrd-tool.json
export OCRD_TOOL_NAME=ocrd-foo-bar
```

(Which you automatically get from [`ocrd__wrap`](#ocrd__wrap).)

### `ocrd__show_resource`

Output given resource file's content.

### `ocrd__list_resources`

Output all resource files' names.

### `ocrd__usage`

Print help on CLI usage.

### `ocrd__parse_argv`

Parses arguments according to [OCR-D CLI](https://ocr-d.de/en/spec/cli).
In doing so, depending on the values passed to it, may delegate to …
- [`ocrd__raise`](#ocrd__raise) and exit (if something went wrong)
- [`ocrd__usage`](#ocrd__usage) and exit
- [`ocrd__dumpjson`](#ocrd__dumpjson) and exit
- [`ocrd__show_resource`](#ocrd__show_resource) and exit
- [`ocrd__list_resources`](#ocrd__list_resources) and exit
- [`ocrd validate tasks`](#ocrd-cli) and return

Expects an associative array ("hash"/"dict") **`ocrd__argv`** to be predefined:

    declare -A ocrd__argv=()

This will be filled by the parser along the following keys:
- `overwrite`: whether `--overwrite` is enabled
- `profile`: whether `--profile` is enabled
- `profile_file`: the argument of `--profile-file`
- `log_level`: the argument of `--log-level`
- `mets_file`: absolute path of the `--mets` argument
- `working_dir`: absolute path of the `--working-dir` argument or the parent of `mets_file`
- `page_id`: the argument of `--page-id`
- `input_file_grp`: the argument of `--input-file-grp`
- `output_file_grp`: the argument of `--output-file-grp`

Moreover, there will be an associative array **`params`**
with the fully expanded runtime values of the ocrd-tool.json parameters.

### `ocrd__wrap`

Parses an [ocrd-tool.json](https://ocr-d.de/en/spec/ocrd_tool) for a specific `tool` (i.e. processor `executable`).

Delegates to …
- [`ocrd__parse_argv`](#ocrd__parse_argv), creating the `ocrd__argv` associative array
- [`ocrd bashlib input-files`](#ocrd-cli), creating the data structures used by [`ocrd__input_file`](#ocrd__input_file)

Usage: `ocrd__wrap PATH/TO/OCRD-TOOL.JSON EXECUTABLE ARGS`

For example:

    ocrd__wrap $SHAREDIR/ocrd-tool.json ocrd-olena-binarize "$@"
    ...

### `ocrd__input_file`

(Requires [`ocrd__wrap`](#ocrd__wrap) to have been run first.)

Access information on the input files according to the parsed CLI arguments:
- their file `url` (or local file path)
- their file `ID`
- their `mimetype`
- their `pageId`
- their proposed corresponding `outputFileId` (generated from `${ocrd__argv[output__file_grp]}` and input file `ID`)

Usage: `ocrd__input_file NR KEY`

For example:

    pageId=`ocrd__input_file 3 pageId`

To be used in a **loop over all selected pages**:

    for ((n=0; n<${#ocrd__files[*]}; n++)); do
        local in_fpath=($(ocrd__input_file $n url))
        local in_id=($(ocrd__input_file $n ID))
        local in_mimetype=($(ocrd__input_file $n mimetype))
        local in_pageId=($(ocrd__input_file $n pageId))
        local out_id=$(ocrd__input_file $n outputFileId)
        local out_fpath="${ocrd__argv[output_file_grp]}/${out_id}.xml
        
        # process $in_fpath to $out_fpath ...
        
        declare -a options
        if [ -n "$in_pageId" ]; then
            options=( -g $in_pageId )
        else
            options=()
        fi
        if [[ "${ocrd__argv[overwrite]}" == true ]];then
            options+=( --force )
        fi
        options+=( -G ${ocrd__argv[output_file_grp]}
                   -m $MIMETYPE_PAGE -i "$out_id"
                   "$out_fpath" )
        ocrd -l ${ocrd__argv[log_level]} workspace -d ${ocrd__argv[working_dir]} add "${options[@]}"

> **Note**: If the `--input-file-grp` is **multi-valued** (N fileGrps separated by commas),
> then usage is similar:
> * The function `ocrd__input_file` can be used, but
>   its results will be **lists** (delimited by whitespace and surrounded by single quotes), 
>   e.g. `[url]='file1.xml file2.xml' [ID]='id_file1 id_file2' [mimetype]='application/vnd.prima.page+xml image/tiff' ...`.
> * Therefore its results should be encapsulated in a (non-associative) **array variable**
>   and without extra quotes, e.g. `in_file=($(ocrd__input_file 3 url))`, or as shown above.
> * This will yield the first fileGrp's results on index 0, 
>   which in bash will always be the same as if you referenced the array without index
>   (so code does not need to be changed much), e.g. `test -f $in_file` which equals `test -f ${in_file[0]}`.
> * Additional fileGrps will have to be fetched from higher indexes, e.g. `test -f ${in_file[1]}`.


## Testing

Download assets (`make assets`)

Test with local files: `make test`

- Test with remote assets:
  - `make test OCRD_BASEURL='https://github.com/OCR-D/assets/raw/master/data/'`

## See Also

  - [OCR-D Specifications](https://https://ocr-d.de/en/spec/) ([Repo](https://github.com/ocr-d/spec))
  - [OCR-D core API documentation](https://ocr-d.de/core) (built here via `make docs`)
  - [OCR-D Website](https://ocr-d.de) ([Repo](https://github.com/ocr-d/ocrd-website))
