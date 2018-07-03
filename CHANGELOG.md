Change Log
==========

Versioned according to [Semantic Versioning](http://semver.org/).

## Unreleased

Fixes:

  * CLI: `-k` on `workspace find` for non-existant fields, #133
  * CLI: Persist downloads in METS, #136

## [0.4.3] - 2018-06-27

Fixed:

  * bash 4.3 compat fixes, #131
  * `ocrd workspace find` default was wrong, #130

## [0.4.2] - 2018-06-25

Added:

   * CLI: `-k` on `workspace find` repeatable

Changed:

   * Simplified bashlib


## [0.4.1] - 2018-06-22

Changed:

  * CLI: rename `workspace create` -> `workspace init` and align with clone syntax

## [0.4.0] - 2018-06-18

Changed:

  * Caching is disabled by default

Added:

  * CLI: `ocrd ocrd-tool version` to show version
  * API: `OcrdMets` getters/setters for `unique_identifier`
  * CLI: `ocrd workspace set-id MODS_IDENTIFIER_PURL` to set mods:identifier
  * CLI: `ocrd workspace get-id` to get mods:identifier
  * CLI: `ocrd workspace clone` syntax changed
  * CLI: `ocrd workspace clone/find` support downloading files
  * CLI: `ocrd workspace find -L` for local files
  * CLI: `ocrd workspace find -i ID` to search by ID

## [0.3.2] - 2018-06-19

Fixed:

  * CLI: `cord ocrd-tool tool parse-params` validate as well as merges with default
  * Parameter validation: Check whether parameter is `required: true`

## [0.3.1] - 2018-06-18

Added

  * CLI support `--version`

Fixed:

  * CLI: validate of ocrd-tool.json didn't parse JSON, #115

Changed:

  * `mets_file_id` in utils is now `concat_padded` and more flexible

## [0.3.0] - 2018-06-18

Added

  * find_files supports `ID`

Changed

  * Adding a file with an existing `ID` will raise an exception, #110

Fixed

  * Wrapped tools support `-J`/`--dump-json`
  * `GROUPID` was not passed when adding files

Removed

  * `--output-mets`, spec v2.0.0

## [0.2.5] - 2018-06-18

Added
  * Bash library
  * CLI command `ocrd-tool`
  * CLI command `workspace find`
  * CLI command `workspace list-group`
  * CLI command `workspace create`
  * CLI `workspace` flag --no-cache
  * bash library to build wrappers
  * CLI: `--version` global flag
Changed
  * Downloading a file will set the URL in the METS
Fixed
  * run_processor will save_mets after process

## [0.2.4] - 2018-06-04

Fixed
  * `GT` is a valid category for mets `fileGrp@USE`

Changed:
  * Adapted to spec v1.2.0


## [0.2.3] - 2018-05-17

#79

Fixed:
  * Adapted to spec v1.1.5
  * Ensure python 2.7 backwards compatibility

Changed:
  * ocrd_tool must be passed to `Processor` constructor

## [0.2.2] - 2018-05-15

Added:
  * points_from_x0y0x1y1 util

Fixed:
  * EXIF tags for PNG


## [0.2.1] - 2018-05-08

Added
  * CLI: `ocrd workspace {add,clone,pack,unpack,validate}`, #75


## [0.2.0] - 2018-05-08

Changed:
  * Use 2018 PAGE namespace http://schema.primaresearch.org/PAGE/gts/pagecontent/2018-07-15, PRImA-Research-Lab/PAGE-XML#4

## [0.1.0] - 2018-04-26

Changed:
  * ocrd_page API based on XSD
  * rename/fix coordinate code

## [0.0.7] - 2018-04-18

Changed
  * Adapted schemas to v1.1.1 of OCR-D/spec

## [0.0.6] - 2018-04-18

Changed
  * Support parameters in run_processor

## [0.0.5] - 2018-04-18

Changed
  * Adapted schemas to v1.1.0 of OCR-D/spec

## [0.0.4] - 2018-04-18

Changed
  * Adapted click wrapper in decorators to v1.0.0 of OCR-D/spec

## [0.0.2] - 2018-04-17

Fixed
  * setup.py install_requires mirrors requirements.txt

## [0.0.1] - 2018-04-17

Initial Release

<!-- link-labels -->
[0.4.3]: ../../compare/v0.4.3...v0.4.2
[0.4.2]: ../../compare/v0.4.2...v0.4.1
[0.4.2]: ../../compare/v0.4.2...v0.4.1
[0.4.1]: ../../compare/v0.4.1...v0.4.0
[0.4.0]: ../../compare/v0.4.0...v0.3.2
[0.3.2]: ../../compare/v0.3.2...v0.3.1
[0.3.1]: ../../compare/v0.3.1...v0.3.0
[0.3.0]: ../../compare/v0.3.0...v0.2.5
[0.2.5]: ../../compare/v0.2.5...v0.2.4
[0.2.4]: ../../compare/v0.2.3...v0.2.4
[0.2.3]: ../../compare/v0.2.2...v0.2.3
[0.2.2]: ../../compare/v0.2.1...v0.2.2
[0.2.1]: ../../compare/v0.2.0...v0.2.1
[0.2.0]: ../../compare/v0.1.0...v0.2.0
[0.1.0]: ../../compare/v0.0.7...v0.1.0
[0.0.7]: ../../compare/v0.0.6...v0.0.7
[0.0.6]: ../../compare/v0.0.5...v0.0.6
[0.0.5]: ../../compare/v0.0.4...v0.0.5
[0.0.4]: ../../compare/v0.0.2...v0.0.4
[0.0.2]: ../../compare/v0.0.1...v0.0.2
[0.0.1]: ../../compare/HEAD...v0.0.1
