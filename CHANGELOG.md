Change Log
==========

Versioned according to [Semantic Versioning](http://semver.org/).

## Unreleased

Changed:

  * bashlib: check bash version to be >= 4.4, #445, OCR-D/ocrd_olena#30
  * `ocrd workspace add` supports `-C`/`--check-file-exists` to validate that `FNAME` is an existing local file, #495
  * `OcrdFile` constructor accepts `ID` parameter
  * `model_factory.page_from_image` now sets the `@pcGtsId` attribute tot the file's `@ID`, #378
  * `WorkspaceValidator`:  check `pc:PcGts/@pcGtsId` == `mets:file/@ID`, #378
  * `OcrdFile` constructor: removed long-obsolete `instance` parameter
  * METS: reorder elements according to schema in empty METS, #487

## [2.8.1] - 2020-06-06

Changed:

  * `OcrdMets.remove_file` now supports all the options of `OcrdMets.find_files`, #497, #458
  * `OcrdMets.remove_file_group` now supports the `USE` param being a regex,, #497, #458

Added:

  * `OcrdMets.remove_one_file`: remove a single `OcrdFile`, either directly or by ID, #497, #458

## [2.8.0] - 2020-06-04

Added:

  * `ocrd-dummy`, a minimal processor that copies input to output, #468
  * OcrdPage: `get_AllRegions`: retrieve all regions, sorted by document or reading order, #479
  * OcrdPage: `sort_AllIndexed`: sort all children by `@index`  in-place
  * OcrdPage: `clear_AllIndexed`: clear all `@index` children
  * OcrdPage: `extend_AllIndexed`: Add elements with incrementing `@index`
  * OcrdPage: Replace empty reading order groups with equivalent `RegionRef` on export
  * OcrdPage: `get_UnorderedGroupChildren`: get reading order elements of an `UnorderedGroup`


Changed:

  * OcrdPage: `get_AllIndexed`: allow filtering by child type
  * OcrdPage: `get_AllIndexed`: index_sort parameter to enable/disable sorting

## [2.7.1] - 2020-05-27

Fixed:

  * `ocrd workspace find`: Use `OcrdMets.get_physical_pages` method, fix #491

## [2.7.0] - 2020-05-27

Changed:

   * :fire: `Workspace.image_from_page` no longer treats `PrintSpace` as functionally equivalent to `Border`, #490
  * `OcrdMets.get_physical_pages` method companion to `OcrdMets.physical_pages` property, #484
  * OcrdMets/ocrd workspace find: Search for multiple pages by fileid, ht @bertsky, #463, #484
  * PAGE validation: respect reading order in consistency checks, #442

## [2.6.1] - 2020-05-14

Added:

  * OcrdPage: new method `get_AllIndexed` for OrderedGroup and OrderedGroupIndexed that lists
    their children, sorted by index, #478

Changed:

  * Improved log message for profiling processors, #477

Fixed:

  * Search for `--page-id` now orders of magnitutde faster, ht @bertsky, #481
  * Not all generateDS types were exported by ocrd_page, now they are, #480


## [2.6.0] - 2020-05-12

Fixed:

  * image files no longer cached in workspace, #446, #448

Added

  * Many mets:file search fields support regex now, #458, #448

## [2.5.3] - 2020-04-30

Fixed:

  * OcrdPage: hacks to make XML namespace output consistent, #474

## [2.5.2] - 2020-04-29

Fixed:

  * logging: format is spec-conformant again, #466

Added:

  * ocrd_page: generateDS-generated code has `__hash__` method now, #443

## [2.5.1] - 2020-04-23

Fixed:

  * logging: disable propagation for loggers with handler, #463

## [2.5.0] - 2020-04-23

Changed:

  * Logging configuration via configuration file, not script, #460 (HT @M3ssman @bertsky)

Added:

  * Execution of processors is tracked with logger 'orcd.process.profile', #461

## [2.4.4] - 2020-03-17

Fixed:

  * #437 broke simple types in PAGE model, (really) revert 3a0a3a8, #451

## [2.4.3] - 2020-03-12

Fixed:

  * bashlib: ocrd-tool.json-related errors no longer lead to silent exit, #456
  * #437 broke simple types in PAGE model, revert 3a0a3a8, #451

## [2.4.2] - 2020-02-20

Fixed:

  * JSON strings longer than OS-allowed filename size crash fixed, #444

## [2.4.1] - 2020-02-19

Changed:

  * Updated PAGE bindings generated using generateDS, #437

## [2.4.0] - 2020-02-17

Fixed:

  * concatenation of PAGE elements was based on `@index` starting with `1`, #430
  * CLI: `--help` should work for processors w/o `input_file_grp`, #440
  * CLI: `--version` more robust, #433

Changed:

  * processor `--help` lists parameter enum values if available, #427
  * :fire: `workspace.save_image_file` takes `mimetype` instead of `format`, #441

## [2.3.1] - 2020-01-23

Changed:

  * More expressive coordination validation, #418
  * `ocrd workspace init` shortcut for `ocrd workspace init .`, #419
  * `ocrd workspace validate` shortcut for `ocrd workspace validate mets.xml`, #419
  * `ocrd workspace clone <METS_URL>` shortcut for `ocrd workspace <METS_URL> .`, #419
  * workspace validation: check of dimensions in image and PAGE only with `--download`, #423
  * behavior of `clobber_mets=False` changed to silently skip re-downloading METS instead of making a fuss, #425

Fixed:

  * regression from #419 for `ocrd workspace validate`
  * regression from #384 for task sequence validation, #424

## [2.3.0] - 2020-01-21

Changed:

  * layout of --help, #411
  * OcrdMets: Removing the last file for a physical page will remove the physical page

Fixed:

  * `mets_basename` was not respected in `ocrd workspace init`, #415, #417
  * typos, #414

Added:

  * OcrdMets.remove_physical_page to remove `structMap[@TYPE="physical"]` entries
  * `ocrd validate` CLI to validate task groups, PAGE XML and processor parameters, #245, #384

## [2.2.2] - 2020-01-16

Added:

  * Validation of input/output file groups before running a processor/task sequence, #392
  * Improved `--help` for both python and bashlib processors, #402, #408

Fixed:

  * bashlib: Calling bashlib processor w/o parameters, #381, #400
  * bashlib: syntax error, regression from 2d89c22ae3. #410

## [2.2.1] - 2020-01-14

Fixed:

  * OcrdExif: PNG metadata extraction was broken, #395, #396
  * Remove the trivial and error-prone  image caching feature in resolver, #399
  * When creating files with workspace.add_file, single-component file paths (i.e. just the basename of a file) were treated as directories, #404
  * When downloading files to a workspace, check first whether those files to be added already exist on disk and are within the workspace directory., #404

## [2.2.0] - 2020-01-10

Fixed:

  * PIL.Image.open'ed files weren't closed, #390
  * resolver: if mets_url is relative path, resolve before anything else, #319, #397
  * Resolver.workspace_from_url: Create dst_dir before resolve for py `<=` 3.5, #330, #393
  * fix help string for -m/--mets, fix #263, #391

Changed:

  * downgrade filegrp syntax errors to warnings, #364, #389

## [2.1.3] - 2020-01-08

Changed:

  * bagit-profile matches changes from spec v3.4.2 (metadata dir)

## [2.1.2] - 2020-01-06

Changed:

  * have save_mets use UTF-8 encoding for byte-serialization (no entities), #388

Fixed:

  * regression from #374, #387

## [2.1.1] - 2020-01-02

Added:

  * PAGE validator: coordinate self-validity and mutual consistency, #374

Fixed:

  * Add more related mime types and fix image/jpeg, #382

## [2.1.0] - 2019-12-20

Added:

  * Workspace validation will check cardinality of images per file is 1, #243, OCR-D/spec#132

Changed:
  
  * bashlib will no longer warn about "non-conformant" file group names, #365
  * Invalid `file:/` URL will now raise exceptions, #373
  * image_from_*: increase tolerance for size mismatch after rotation to 2px, #371

## [2.0.2] - 2019-12-02

Changed:

  * `ocrd process`: Validate parameters when validating a task
  * Dockerfile: Revert to Ubuntu 18.04 for LTS compatibility, #344
  * Parameter validation: Raise exception for unknown parameters
  * `ocrd ocrd-tool validate`: Raise exception for unknown keys in JSON

## [2.0.1] - 2019-11-26

Fixed:

  * METS `CREATEDATE` date format now ISO8601, #360
  * `ocrd workspace find` allow outputting file group, #359
  * processor decorator: `--version` should succeed independent of parameters, #358

Changed:

  * `ocrd process` uses the ocrd-tool.json of the tools to check whether output file group necessary, #296
  * Dockerfile: Revert to Ubuntu 18.04 for LTS compatibility, #344
  * pixel density warnings downgraded further to "notice", #361

## [2.0.0] - 2019-11-05

Changed:

  * image_from_page etc: allow filling with background or transparency
  * :fire: API changes, #311, #327
  * Dockerfile: Omit `ENTRYPOINT`, OCR-D/spec#130, #340
  * Relax pixel density validation errors to warnings, OCR-D/spec#129, #339

## [1.0.1] - 2019-10-25

Fixed:

  * Add `dimension` to workspace validation skip list, #329
  * Update ocrd-tool.json schema to spec 3.3.0 (no output_file_grp, no syntax restriction on content-type)
  * PAGE XML output references xsi:schemaLocation, #331
  * Update Pillow to 6.2.0

Changed:
  * `ocrd process`: task validation takes processor's ocrd-tool into account, #296

## [1.0.0] - 2019-10-18

* Workspace validation: Validate that files mentioned in pc:Page/@imageFilename exist in METS and on FS, #309
* `ocrd ocrd-tool parse-params` has the string-or-filepath logic for -p/--parameter as for the [CLI](https://ocr-d.github.io/cli#-p---parameter-param_json)

## [1.0.0b19] - 2019-09-10

* image_from_page etc: allow filtering by feature (@comments), #294

## [1.0.0b18] - 2019-09-06

Changed:

  * `-m/--mets` is not required anymore, #301
  * `ocrd workspace prune-files`: Throw on error removing non-existent file
  * `-p/--parameter` argument accepts raw JSON as well now, #239

Fixed:

  * OcrdFile: Default fileGrp to `TEMP`
  * OcrdFile: Accept url constructor arg
  * Workspace: Simplify file download code, add extensions to files
  * Processor: `chdir` to workspace directory on init so relative files resolve properly
  * typos in docstrings
  * README: 'module' -> 'package'
  * workspace.image_from_page etc: logic with rotation/angle
  * Adapted test suite to OCR-D/assets now with file extensions

Added:

  * utils: `MIME_TO_EXT` to map mime types to preferred extension
  * Validation of imageHeight/imageWidth in PAGE vs. actual image height/width, #229

## [1.0.0b17] - 2019-08-21

Fixed:

  * Require `Pillow == 5.4.1` throughout

## [1.0.0b16] - 2019-08-21

Added:

  * many utility methods for image manipulation and coordinate handling, #268, OCR-D/ocrd_tesserocr#49
    * `bbox_from_points`
    * `bbox_from_xywh`
    * `bbox_from_polygon`
    * `coordinates_for_segment`
    * `coordinates_of_segment`
    * `crop_image`
    * `membername`
    * `image_from_polygon`
    * `points_from_bbox`
    * `points_from_polygon`
    * `points_from_xywh`
    * `polygon_from_bbox`
    * `polygon_from_x0y0x1y1`
    * `polygon_from_xywh`
    * `polygon_mask`
    * `rotate_coordinates`
    * `xywh_from_bbox`
  * Spec-conformant handling of AlternativeImage, OCR-D/spec#116, OCR-D/ocrd_tesserocr#33, #284

Changed:

  * workspace bagger will create files with extension
  * `save_mets` is atomic now, #278, #285

## [1.0.0b15] - 2019-08-14

Fixed:

  * regression in namespace handling of PAGE output, #277

## [1.0.0b14] - 2019-08-14

Fixed:

  * METS is serialized as Unicode instead of character entities, #279

## [1.0.0b13] - 2019-08-13

Added:

  * `ocrd workspace remove` to remove files, #275, #245
  * `ocrd workspace remove-group` to remove file groups, #275, #245
  * `ocrd workspace prune-files`

## [1.0.0b12] - 2019-08-08

Fixed:

  * Regression with ocrd_page data types, #269
  * Segfault issue with Pillow >= 6.0.0, #270

## [1.0.0b11] - 2019-07-29

Changed:

  * Improve pixel density logic in OcrdExif, #256, #37, OCR-D/ocrd_tesserocr#54
  * :fire: stop supporting python `<= 3.4`
  * Support only 2019-07-15 PAGE version

## [1.0.0b10] - 2019-06-25

Fixed:

  * Handle TIFF ResolutionUnit not being set #250
  * bashlib: `--mets-file` should be `--mets`

Changed:

  * missing required parameters should raise exception, fix #244 #247

## [1.0.0b9] - 2019-05-20

Changed:

  * export additional region types from generated code, #241

## [1.0.0b8] - 2019-03-24

Added:

  * `points_from_y0x0y1x1` for inverted x/y pairs

## [1.0.0b7] - 2019-03-24

Added:

  * `ocrd workspace list-page` to list all page IDs

Changed:
  * Extended page with TextStyle for Page, , PRImA-Research-Lab/PAGE-XML#8

## [1.0.0b6] - 2019-03-19

  * `ocrd workspace set-id` case in argument error
  * fix DeprecationWarning for PyYAML 5.1+
  * use headless opencv

## [1.0.0b1] - 2019-02-27

First beta of 1.0.0

Changed:

  * :fire: Drop Python2 support
  * :fire: Refactored project into 5 modules with little dependencies each
  * Implement 3.2.0 of the spec

Removed:

  * :fire: Move factory methods from OcrdPage and OcrdExif to new module `ocrd.model_factory`
  * Factor out XML constants to `ocrd.constants.xml`
  * :fire: BaseProcessor.add_output_file removed


## [0.15.2] - 2019-01-07

Added:

  * workspace validator: make url tests (java, non-http) checks skippable

## [0.15.1] - 2019-01-04

Fixed:

  resolver: fall back to "mets.xml" as basename if not provided

## [0.15.0] - 2018-12-20

Added:

  * PageValidator: Check consistency of PAGE according to spec 3.0.0, #223

Changed:

  * :fire: Change validators to use a single static `validate` method where applicable, #224

## [0.14.0] - 2018-12-13

Changed:

  * :fire: Use mets:structMap[@TYPE="PHYSICAL"] instead of GROUPID to group by page, #221, #222, OCR-D/spec#81
  * :fire: Rename group_id -> page_id, throughout, OCR-D/spec#101
  * :fire: CLI: Rename --group-id -> --page-id (`-g`)

## [0.13.3] - 2018-12-05

Fixed:

  * `ocrd workspace clone` fixed to have the pre-0.13.1 behavior
  * Missing metsHdr made adding agents fail, #218

## [0.13.2] - 2018-11-29

Changed:

  * various fixes to workspace and OCRD-ZIP validation, #217

## [0.13.1] - 2018-11-26

Fixed:

  * Relative files in workspace were resolved to target, not source dir of METS, #215

## [0.13.0] - 2018-11-23

Changed:

  * Adapt bagit profile to spec v2.6.2: allow fetch.txt
  * Adapt bagit profile to spec v2.6.3: Tag-Files-Allowed

Removed:

  * Code related to generating Open API / Swagger definitions, #210

## [0.12.0] - 2018-11-22

Changed:

  * Depend on pillow >= 5.3.0 to mitigate https://github.com/python-pillow/Pillow/issues/2926

Added:

  * backup functionality for `ocrd workspace`, #204

## [0.11.0] - 2018-11-21

Changed:

  * `ocrd process` interface change, #205

Fixed:

  * Grayscale images can be handled by workspace correctly now, #211

## [0.10.0] - 2018-11-15

Added:

  * OCRD-ZIP implementation based on OCR-D/spec#70, #207
  * CLI: `ocrd zip` to bag, spill and validate OCRD-ZIP

Fixed:

  * Adapted tests to work with bagit-based structure, OCR-D/assets#18
  * Read `VERSION` constant from setup.py, #209

## [0.9.0] - 2018-10-30

Fixed:

  * CLI: `ocrd process`, #199

Changed:

  * Implement changes from spec v2.5.0: ocrd-tool must have in/output groups

## [0.8.8] - 2018-10-24

Fixed:

  * `KeyError` because ocrd_tool not saved on processor instance, #192
  * another `KeyError` because `pnginfo` isn't set for all PNG by exiftool, #194
  * support 1-bit bitonal images, #196

## [0.8.7] - 2018-10-23

Changed:

  * Calling `workspace.save_mets()` will now save processor information in the header, #147, #191

## [0.8.6] - 2018-10-19

Changed:

  * Update ocrd-tool schema to spec v2.4.0

Fixed:

  * Calls to `click.argument` had too many arguments, #186

## [0.8.5] - 2018-09-26

Changed:

  * Logger setup according to v2.3.0 of the spec, #185

## [0.8.4] - 2018-09-21

Removed:

  * remove `workspace_from_folder`, #180

Changed:

  * Creating METS from scratch will set creator agent and creation date, #147

Fixed:

  * Schema regression in 0.8.3 (description)

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

  * CLI: `-k` on `workspace find` for non-existent fields, #133
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
[2.8.1]: ../../compare/v2.8.1...v2.8.0
[2.8.0]: ../../compare/v2.8.0...v2.7.1
[2.7.1]: ../../compare/v2.7.1...v2.7.0
[2.7.0]: ../../compare/v2.7.0...v2.6.1
[2.6.1]: ../../compare/v2.6.1...v2.6.0
[2.6.0]: ../../compare/v2.6.0...v2.5.3
[2.5.3]: ../../compare/v2.5.3...v2.5.2
[2.5.2]: ../../compare/v2.5.2...v2.5.1
[2.5.1]: ../../compare/v2.5.1...v2.5.0
[2.5.0]: ../../compare/v2.5.0...v2.4.4
[2.4.4]: ../../compare/v2.4.4...v2.4.3
[2.4.3]: ../../compare/v2.4.3...v2.4.2
[2.4.2]: ../../compare/v2.4.2...v2.4.1
[2.4.1]: ../../compare/v2.4.1...v2.4.0
[2.4.0]: ../../compare/v2.4.0...v2.3.1
[2.3.1]: ../../compare/v2.3.1...v2.3.0
[2.3.0]: ../../compare/v2.3.0...v2.2.2
[2.2.2]: ../../compare/v2.2.2...v2.2.1
[2.2.1]: ../../compare/v2.2.1...v2.2.0
[2.2.0]: ../../compare/v2.2.0...v2.1.3
[2.1.3]: ../../compare/v2.1.3...v2.1.2
[2.1.2]: ../../compare/v2.1.2...v2.1.1
[2.1.1]: ../../compare/v2.1.1...v2.1.0
[2.1.0]: ../../compare/v2.1.0...v2.0.2
[2.0.2]: ../../compare/v2.0.2...v2.0.1
[2.0.1]: ../../compare/v2.0.1...v2.0.0
[2.0.0]: ../../compare/v2.0.0...v1.0.1
[1.0.1]: ../../compare/v1.0.1...v1.0.0
[1.0.0]: ../../compare/v1.0.0...v1.0.0b19
[1.0.0b19]: ../../compare/v1.0.0b19...v1.0.0b18
[1.0.0b18]: ../../compare/v1.0.0b18...v1.0.0b17
[1.0.0b17]: ../../compare/v1.0.0b17...v1.0.0b16
[1.0.0b16]: ../../compare/v1.0.0b16...v1.0.0b15
[1.0.0b15]: ../../compare/v1.0.0b15...v1.0.0b14
[1.0.0b14]: ../../compare/v1.0.0b14...v1.0.0b13
[1.0.0b13]: ../../compare/v1.0.0b13...v1.0.0b12
[1.0.0b12]: ../../compare/v1.0.0b12...v1.0.0b11
[1.0.0b11]: ../../compare/v1.0.0b11...v1.0.0b10
[1.0.0b10]: ../../compare/v1.0.0b10...v1.0.0b9
[1.0.0b9]: ../../compare/v1.0.0b9...v1.0.0b6
[1.0.0b6]: ../../compare/v1.0.0b6...v1.0.0b1
[1.0.0b1]: ../../compare/v1.0.0b1...v0.15.2
[0.15.2]: ../../compare/v0.15.2...v0.15.1
[0.15.1]: ../../compare/v0.15.1...v0.15.0
[0.14.0]: ../../compare/v0.14.0...v0.13.3
[0.13.3]: ../../compare/v0.13.3...v0.13.2
[0.13.2]: ../../compare/v0.13.2...v0.13.1
[0.13.1]: ../../compare/v0.13.1...v0.13.0
[0.13.0]: ../../compare/v0.13.0...v0.12.0
[0.12.0]: ../../compare/v0.12.0...v0.11.0
[0.11.0]: ../../compare/v0.11.0...v0.10.0
[0.10.0]: ../../compare/v0.10.0...v0.9.0
[0.9.0]: ../../compare/v0.9.0...v0.8.8
[0.8.8]: ../../compare/v0.8.8...v0.8.7
[0.8.7]: ../../compare/v0.8.7...v0.8.6
[0.8.6]: ../../compare/v0.8.6...v0.8.5
[0.8.5]: ../../compare/v0.8.5...v0.8.4
[0.8.4]: ../../compare/v0.8.4...v0.8.3
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
