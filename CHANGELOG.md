Change Log
==========

Versioned according to [Semantic Versioning](http://semver.org/).

## Unreleased


Removed:

  * remove `workspace_from_folder`, #180

Changed:

  * Creating METS from scratch will set creator agent and creation date, #147


## [0.8.3] - 2018-09-20

Changed:

  * Make logging logic spec-compliant according to #173

Removed:

  * `prefer_symlink` mechanism, #179

## [0.8.2] - 2018-09-04

Fixed:

  * Handle missing parameters in ocrd-tool.json like empty array #160
  * cli: `ocrd workspace validate` #175

## [0.8.1] - 2018-08-31

Removed:

  * `merge_ocr_txt.py` script to be reborn as its own project, #170

## [0.8.0] - 2018-08-22

Fixed:

  * file://-URL will not be "downloaded" if already present, #165

Changed:

  * Logging can be configured with a file `ocrd_logging.py` in either $PWD, $HOME or /etc, #164
  * `Processor.add_output_file` deprecated, #166

## [0.7.5] - 2019-08-16

Fixed:

  * bashlib: invalid parsers caused cryptic error, #161

## [0.7.4] - 2019-08-15

Fixed:

  * Sort coordinates clockwise, #159, https://github.com/OCR-D/assets/issues/11

## [0.7.3] - 2019-08-14

Changed:

  * Missing `description` for parameters in schema, #155

## [0.7.2] - 2019-08-01

Fixed

  * Regression in XML pretty printing, #152

## [0.7.1] - 2019-07-25

Changed:

  * Remove dependency on `xmllint` command line tool, #72, #151
  * Remove dependency on `exiftool`, #71, #150

## [0.7.0] - 2018-07-25

Changed:

  * Behavior of workspace generation from URL changes (#149)
    * when cloning from a `file://` URL and no directory is given do NOT create
      a temporary directory but reuse the existing directory
    * When not providing `mets_basename`, assume the last URL path segment to be
      the METS basename instead of the fixed string `mets.xml`
  * incoroporate changes to ocrd_tool schema from spec/v2.2.1

## [0.6.0] - 2018-07-23

Changed:

  * Harmonized URL handling according to https://ocr-d.github.io/cli#urlfile-convention / spec v2.2.0

## [0.5.0] - 2018-07-19

Fixed:

  * EXIF supports JFIF metadata, #141
  * typo: repository -> workspace

Changed:

  * sh wrapper: set `working_dir` always, default to `$PWD`
  * Drop all caching, #132, #143, #126, #100, #92, #45, #85

Added:

  * CLI: `--force` option for `workspace add` to replace existing ID, #134

## [0.4.4] - 2018-07-03

Fixes:

  * CLI: `-k` on `workspace find` for non-existant fields, #133
  * CLI: Persist downloads in METS, #136
  * CLI: `workspace find --download` will download to subdir of fileGrp, #137

Added:
  * `OcrdFile` has getter `fileGrp` for the `USE` attribute of parent `mets:fileGrp`, #139

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
[0.8.3]: ../../compare/v0.8.3...v0.8.2
[0.8.2]: ../../compare/v0.8.2...v0.8.1
[0.8.1]: ../../compare/v0.8.1...v0.8.0
[0.8.0]: ../../compare/v0.8.0...v0.7.5
[0.7.5]: ../../compare/v0.7.5...v0.7.4
[0.7.4]: ../../compare/v0.7.4...v0.7.3
[0.7.3]: ../../compare/v0.7.3...v0.7.2
[0.7.2]: ../../compare/v0.7.2...v0.7.1
[0.7.1]: ../../compare/v0.7.1...v0.7.0
[0.7.0]: ../../compare/v0.7.0...v0.6.0
[0.6.0]: ../../compare/v0.6.0...v0.5.0
[0.5.0]: ../../compare/v0.5.0...v0.4.4
[0.4.4]: ../../compare/v0.4.4...v0.4.3
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
