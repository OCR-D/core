Change Log
==========

Versioned according to [Semantic Versioning](http://semver.org/).

## Unreleased

## [3.0.0b5] - 2024-09-16

Fixed:
  - tests: ensure `ocrd_utils.config` gets reset whenever changing it globally
  - `OcrdMetsServer.add_file`: pass on `force` kwarg
  - `ocrd.cli.workspace`: consistently pass on `--mets-server-url` and `--backup`
  - `ocrd.cli.validate "tasks"`: pass on `--mets-server-url`
  - `ocrd.cli.bashlib "input-files"`: pass on `--mets-server-url`
  - `lib.bash input-files`: pass on `--mets-server-url`, `--overwrite`, and parameters
  - `lib.bash`: fix `errexit` handling
  - `ocrd.cli.ocrd-tool "resolve-resource"`: forgot to actually print result

Changed:
  - :fire: `Processor` / `Workspace.add_file`: always `force` if `OCRD_EXISTING_OUTPUT==OVERWRITE`
  - :fire: `Processor.verify`: revert 3.0.0b1 enforcing cardinality checks (stay backwards compatible)
  - :fire: `Processor.verify`: check output fileGrps, too
     (must not exist unless `OCRD_EXISTING_OUTPUT=OVERWRITE|SKIP` or disjoint `--page-id` range)
  - lib.bash `input-files`: do not try to validate tasks here (now covered by `Processor.verify()`)
  - `run_processor`: be robust if `ocrd_tool` is missing `steps`
  - `PcGtsType.PageType.id` via `make_xml_id`: replace `/` with `_`

Added:
  - `OcrdPage`: new `PageType.get_ReadingOrderGroups()` to retrieve recursive RO as dict
  - ocrd.cli.workspace `server`: add subcommands `reload` and `save`
  - METS Server: export and delegate `physical_pages`
  - processor CLI: delegate `--resolve-resource`, too
  - `Processor.process_page_file` / `OcrdPageResultImage`: allow `None` besides `AlternativeImageType`

## [3.0.0b4] - 2024-09-02

Fixed:

  * `Processor.metadata_location`: `src` workaround respects namespace packages, qurator-spk/eynollah#134
  * `Workspace.reload_mets`: handle ClientSideOcrdMets as well

## [3.0.0b3] - 2024-08-30

Added:

  * `OcrdConfig.reset_defaults` to reset config variables to their defaults

## [3.0.0b2] - 2024-08-30

Added:
 - `Processor.max_workers`: class attribute to control per-page parallelism of this implementation
 - `Processor.max_page_seconds`: class attribute to control per-page timeout of this implementation
 - `OCRD_MAX_PARALLEL_PAGES` for whether and how many workers should process pages in parallel
 - `OCRD_PROCESSING_PAGE_TIMEOUT` for whether and how long processors should wait for single pages
 - `OCRD_MAX_MISSING_OUTPUTS` for maximum rate (fraction) of pages before making `OCRD_MISSING_OUTPUT=abort`

Fixed:
  - `disableLogging`: also re-instate root logger to Python defaults

## [3.0.0b1] - 2024-08-26

Fixed:
  - actually apply CLI `--log-filename`, and show in `--help`
  - adapt to Pillow changes
  - `ocrd workspace clone`: do pass on `--file-grp` (for download filtering)

Changed:
  - :fire: `ocrd_utils`, `ocrd_models`, `ocrd_modelfactory`, `ocrd_validators` and `ocrd_network` are not published
    as separate packages anymore, everything is contained in `ocrd` - you should adapt your `requirements.txt` accordingly
  - :fire: `Processor.parameter` now a property (attribute always exists, but `None` for non-processing contexts)
  - :fire: `Processor.parameter` is now a `frozendict` (contents immutable)
  - :fire: `Processor.parameter` validate when(ever) set instead of (just) the constructor
  - setting `Processor.parameter` will also trigger (`Processor.shutdown() and) `Processor.setup()`
  - `get_processor(... instance_caching=True)`: use `min(max_instances, OCRD_MAX_PROCESSOR_CACHE)`
  - :fire: `Processor.verify` always validates fileGrp cardinalities (because we have `ocrd-tool.json` defaults now)
  - :fire: `OcrdMets.add_agent` without positional arguments
  - `ocrd bashlib input-files` now uses normal Processor decorator, and gets passed actual `ocrd-tool.json` and tool name
    from bashlib's `ocrd__wrap`

Added:
  - `Processor.metadata_filename`: expose to make local path of `ocrd-tool.json` in Python distribution reusable+overridable
  - `Processor.metadata_location`: expose to make absolute path of `ocrd-tool.json` reusable+overridable
  - `Processor.metadata_rawdict`: expose to make in-memory contents of `ocrd-tool.json` reusable+overridable
  - `Processor.metadata`: expose to make validated and default-expanded contents of `ocrd-tool.json` reusable+overridable
  - `Processor.shutdown`: to shut down processor after processing, optional
  - `Processor.max_instances`: class attribute to control instance caching of this implementation

## [3.0.0a2] - 2024-08-22

Changed:
 - :fire: `OcrdPage` as proxy of `PcGtsType` instead of alias; also contains `etree` and `mapping` now
 - :fire: `page_from_file`: removed kwarg `with_tree` - use `OcrdPage.etree` and `OcrdPage.mapping` instead
 - :fire: `Processor.zip_input_files` now can throw `ocrd.NonUniqueInputFile` and `ocrd.MissingInputFile`
   (the latter only if `OCRD_MISSING_INPUT=ABORT`)
 - :fire: `Processor.zip_input_files` does not by default use `require_first` anymore
   (so the first file in any input file tuple per page can be `None` as well)
 - :fire: no more `Workspace.overwrite_mode`, merely delegate to `OCRD_EXISTING_OUTPUT=OVERWRITE`
 - :art: improve on docs result for `ocrd_utils.config`

Added:
  - :point_right: `OCRD_DOWNLOAD_INPUT` for whether input files should be downloaded before processing
  - :point_right: `OCRD_MISSING_INPUT` for how to handle missing input files (**`SKIP`** or `ABORT`)
  - :point_right: `OCRD_MISSING_OUTPUT` for how to handle processing failures (**`SKIP`** or `ABORT` or `COPY`)
     the latter behaves like ocrd-dummy for the failed page(s)
  - :point_right: `OCRD_EXISTING_OUTPUT` for how to handle existing output files (**`SKIP`** or `ABORT` or `OVERWRITE`)
  - new CLI option `--debug` as short-hand for `ABORT` choices above
  - `Processor.logger` set up by constructor already (for re-use by processor implementors)
  - `default`-expand and validate `ocrd_tool.json` in `Processor` constructor, log invalidities
  - handle JSON `deprecation` in `ocrd_tool.json` by reporting warnings

## [3.0.0a1] - 2024-08-15

Changed:
  - :fire: Deprecate `Processor.process`
  - update spec to v3.25.0, which requires annotating fileGrp cardinality in `ocrd-tool.json`
  - :fire: Remove passing non-processing kwargs to `Processor` constructor, add as members  
     (i.e. `show_help`, `dump_json`, `dump_module_dir`, `list_resources`, `show_resource`, `resolve_resource`)
  - :fire: Deprecate passing processing arg / kwargs to `Processor` constructor  
     (i.e. `workspace`, `page_id`, `input_file_grp`, `output_file_grp`; now all set by `run_processor`)
  - :fire: Deprecate passing `ocrd-tool.json` metadata to `Processor` constructor
  - `ocrd.processor`: Handle loading of bundled `ocrd-tool.json` generically

Added:
  - `Processor.process_workspace`: process a complete workspace, with default implementation
  - `Processor.process_page_file`: process an OcrdFile, with default implementation
  - `Processor.process_page_pcgts`: process a single OcrdPage, produce a single OcrdPage, required to implement
  - `Processor.verify`: handle fileGrp cardinality verification, with default implementation
  - `Processor.setup`: to set up processor before processing, optional

## [2.70.0] - 2024-10-10

Added:

  - `ocrd network client workflow run`: Add `--print-status` flag to periodically print the job status, #1277
  - Processing Server: `DELETE /mets_server_zombies` to kill any renegade METS servers, #1277
  - No more zombie METS Server by properly shutting them down, #1284
  - `OCRD_NETWORK_RABBITMQ_HEARBEAT` to allow overriding the [heartbeat](https://pika.readthedocs.io/en/stable/examples/heartbeat_and_blocked_timeouts.html) behavior of RabbitMQ, #1285

Changed:

  - significantly more detailed logging for the METS Server and Processing Server, #1284
  - Only import `ocrd_network` in src/ocrd/decorators/__init__.py once needed, #1289
  - Automate release via GitHub Actions, #1290

Fixed:

  - `ocrd/core-cuda-torch`: Install torchvision as well, #1286
  - Processing Server: remove shut down METS servers from deployer's cache, #1287
  - typos, #1274

## [2.69.0] - 2024-09-30

Fixed:
  - tests: ensure `ocrd_utils.config` gets reset whenever changing it globally
  - `ocrd.cli.workspace`: consistently pass on `--mets-server-url` and `--backup`
  - `ocrd.cli.workspace`: make `list-page` work w/ METS Server
  - `ocrd.cli.validate "tasks"`: pass on `--mets-server-url`
  - `lib.bash`: fix `errexit` handling
  - actually apply CLI `--log-filename`, and show in `--help`
  - adapt to Pillow changes
  - `ocrd workspace clone`: do pass on `--file-grp` (for download filtering)
  - `OcrdMetsServer.add_file`: pass on `force` kwarg
  - `Workspace.reload_mets`: handle ClientSideOcrdMets as well
  - `OcrdMets.get_physical_pages`: cover `return_divs` w/o `for_fileIds` and `for_pageIds`
  - `disableLogging`: also re-instate root logger to Python defaults
  - `OcrdExif`: handle multi-frame TIFFs gracefully in `identify` callout, #1276

Changed:
  - `run_processor`: be robust if `ocrd_tool` is missing `steps`
  - `PcGtsType.PageType.id` via `make_xml_id`: replace `/` with `_`
  - `ClientSideOcrdMets`: use same logger name prefix as METS Server
  - `Processor.zip_input_files`: when `--page-id` yields empty list, just log instead of raise

Added:
  - `OcrdPage`: new `PageType.get_ReadingOrderGroups()` to retrieve recursive RO as dict
  - METS Server: export and delegate `physical_pages`
  - ocrd.cli.workspace `server`: add subcommands `reload` and `save`
  - processor CLI: delegate `--resolve-resource`, too
  - `OcrdConfig.reset_defaults` to reset config variables to their defaults
  - `ocrd_utils.scale_coordinates` for resizing images

## [2.68.0] - 2024-08-23

Changed:

  * ocrd_network: Use `ocrd-all-tool.json` bundled by core instead of download from website, #1257, #1260
  * :fire: `ocrd network client processing processor` renamed `ocrd network client processing run`, #1269
  * `ocrd network client processing run` supports blocking behavior with `--block` by polling job status, #1265, #1269

Added:

  * `ocrd network client workflow run` Run, optionally blocking, a workflow on the processing server, #1265, #1269
  * `ocrd network client workflow check-status` to get the status of a workflow job, #1269
  * `ocrd network client processing check-status` to get the status of a processing (processor) job, #1269
  * `ocrd network client discovery processors` to list the processors deployed in the processing server, #1269
  * `ocrd network client discovery processor` to get the `ocrd-tool.json` of a deployed processor, #1269
  * `ocrd network client processing check-log` to retrieve the log data for a processing job, #1269
  * Environment variables `OCRD_NETWORK_CLIENT_POLLING_SLEEP` and `OCRD_NETWORK_CLIENT_POLLING_TIMEOUT` to control polling interval and timeout for `ocrd network client {processing processor,workflow run`, #1269
  * `ocrd workspace clone`/`Resolver.workspace_from_url`: with `clobber_mets=False`, raise a FileExistsError for existing mets.xml on disk, #563, #1268
  * `ocrd workspace find --download`: print the the correct, up-to-date field, not `None`, #1202, #1266

Fixed:

  * Sanitize `self.imageFilename` for the `pcGtsId` to ensure it is a valid `xml:id`, #1271

## [2.67.2] - 2024-07-19

Fixed:

  * Run `multiprocessing.set_start_method('fork')` only for OSX, #1261
  * Broken PyPI release, #1262

## [2.67.1] - 2024-07-17

Fixed:

  - Build and tests fixed, no functional changes from #1258

## [2.67.0] - 2024-07-16

Changed:

  - Additional docker base images with preinstalled tensorflow 1 (`core-cuda-tf1`), tensorflow 2 (`core-cuda-tf2`) and torch (`core-cuda-torch`), #1239
  - Resource Manager: Skip instead of raise an exception download if target file already exists (unless `--overwrite`), #1246
  - Resource Manager: Try to use bundled `ocrd-all-tool.json` if available, #1250, OCR-D/all#444

Added:

  - `ocrd process` does support `-U/--mets-server`, #1243

Fixed:

  - `ocrd process`-derived tasks are not run in a temporary directory when not called from within workspace, #1243
  - regression from #1238 where processors failed that had required parameters, #1255, #1256
  - METS Server: Unlink UDS sockert file if it exists before startup, #1244
  - Resource Manager: Do not create zero-size files for failing downloads, #1201, #1246
  - Workspace.add_file: Allow multiple processors to create file group folders simultaneously, #1203, #1253
  - Resource Manager: Do not try to run `--dump-json` for known non-processors `ocrd-{cis-data,import,make}`, #1218, #1249
  - Resource Manager: Properly handle copying of directories, #1237, #1248
  - bashlib: regression in parsing JSON from introducing parameter preset files, #1258

Removed:

  - Defaults for `-I/--input-file-grp`/`-O/--output-file-grp`, #1256, #274

## [2.66.1] - 2024-06-26

Fixed:

  * GHA Docker: build docker.io first, then tag ghcr.io

## [2.66.0] - 2024-06-07

Fixed:

  * `OcrdFile.url` can now be removed properly, #1226, #1227
  * `ocrd workspace find --undo-download`: Only remove file refs if it's an actual download, #1150, #1235
  * `ocrd workspace find --undo-download`: When `--keep-files` is not set, remove file from disk, #1150, #1235
  * `OCRD_LOGGING_DEBUG`: Normalize/lowercase boolean values, #1230, #1231
  * `Workspace.download_file`: Use `Ocrd.local_filename` if set but not already present in the FS, #1149, #1228

Changed:

  * Install ocrd with `pip --editable` inside Docker, #1225, OCR-D/ocrd_all#416
  * Reduce log spam in ocrd_network, #1222
  * CI: Stop testing for 3.7, #1207, #1221

Added:

  * Separate docker versions for tensorflow v1, tensorflow v2 and torch, #1186
  * Processing server can serve as a proxy for METS Server TCP requests, forwarding to UDS, #1220
  * `ocrd workspace clean` to remove "untracked", i.e. not METS-referenced, files, #1150, #1236
  * `-p` now supports parameter preset resources in addition to raw JSON and absolute/relative paths to JSON files, #930, #969, #1238

## [2.65.0] - 2024-05-03

Fixed:

  - bashlib processors will download on-demand, like pythonic processors do, #1216, #1217

Changed:

  - Replace `distutils` which equivalents from `shutil` for compatibility with python 3.12+, #1219
  - CI: Updated GitHub actions, #1206
  - CI: Fixed scrutinizer, #1217

Added:

  - Integration tests for `ocrd_network`, #1184

## [2.64.1] - 2024-04-22

Fixed:

  * Broken PyPI release

## [2.64.0] - 2024-04-22

Removed:

  * Support for Python `<=` 3.7, #1207

Fixed:

  * remove duplicate description of `OCRD_DOWNLOAD_TIMEOUT` in `--help`, #1204
  * Use `importlib_metadata` shim for 3.9+, #1210, OCR-D/ocrd_froc#10

## [2.63.3] - 2024-03-07

Added:

  * `make uninstall-workaround` compantion to `make install-workaround`, #119

Fixed:

  * `OcrdMets.add_file`: fix finding existing el_pagediv, #1199


## [2.63.2] - 2024-03-05

Fixed:

  * Missed incrementing version

## [2.63.1] - 2024-03-05

Fixed:

  * `OcrdMets` bug that produced invalid caches, #1192, #1195, #1193

## [2.63.0] - 2024-02-12

Fixed:

  * Reduce logging level of spammy log statements to `DEBUG` in workspace, #1181
  * Clean up lxml code, #1188

Changed:

  * :fire: `OcrdFile.local_filename` returns/accepts `str` after unpopular change to `Path` from #1079, #1182, #1167
  * `WorkspaceValidator`: more efficiency by doing all page checks in the same loop, #1071

Added:

  * `OcrdMets.get_physical_pages` to search for/change/generate ranges for page-specific `mets:div` attributes beyond to `@ID`, #821, #1063

## [2.62.0] - 2024-01-30

Added:

  * Basic integration test for `ocrd_network`, #1164
  * `ocrd-tool.json` for `ocrd-dummy` now in repo root, for ocrd_all's `make ocrd-all-tool.json`, #1168

Fixed:

  * METS Server: UDS sockets are removed on process exit, #117

Changed:

  * replace license-incompatible sparkline library with a simpler implementation, #1176
  * remove all pkg_resources calls with modern alternatives, no more run-time setuptools dependency, #1174

## [2.61.2] - 2024-01-24

Fixed:

  * another regression to docker deployment (requirements.txt missing), #1173

## [2.61.1] - 2024-01-23

Fixed:

  * deps-cuda: add workaround for keras-team/tf-keras#62, #1169
  * fix regression docker deployment, #1172


## [2.61.0] - 2024-01-23

Changed:

  * :fire: simplify the project layout and distribution policy, #1166
    * In the future there will be only one distribution `ocrd`
    * The previous separate distributions of the `ocrd_utils`, `ocrd_models`, `ocrd_modelfactory`, `ocrd_validators` and `ocrd_network` are all part of `ocrd` now
    * Nothing needs to be changed in code using OCR-D/core, the package structure and API is the same as before
    * Until the next major release, we will continue to provide distributions for `ocrd_utils` etc. that contain the same code as `ocrd`
    * Using `ocrd_utils` etc. as distributions in `requirements.txt` or `install_requires` is now deprecated
    * Once we release v3.0.0, these distributions will be depublished

## [2.60.3] - 2024-01-10

Fixed:

  * `make install-dev` working with `setuptools>=64` again, #1163

## [2.60.2] - 2024-01-09

Fixed:

  * Log level downgraded from DEBUG to INFO in logging.conf, #1161
  * log OAI check as `DEBUG` not `INFO`, #1160

## [2.60.1] - 2023-12-15

Fixed:

  * Docker: copy `.git` during build, so `setuptools_scm` can determine version number, #1159

## [2.60.0] - 2023-12-15

Fixed:

  * `ocrd workspace list-page` now works in workspaces with non-page-specific files, #1148, #1151

Changed:

  * `cli.workspace.WorkspaceCtx` and `Resolver.resolve_mets_arguments` now have defaults for `mets_server_url`, `mets_basename` and `automatic_backup`, slub/mets-mods2tei#68, #1156
  * :fire: switch to `pyproject.toml`, derive version from git, separate build from install, #1065

## [2.59.1] - 2023-12-05

Fixed:

  * Chunking algorithm for `ocrd workspace list-page` now handles edge cases properly, #1145
  * Avoid deadlocks in `ocrd_network` if processing workers not deployed, #1125, #1142

## [2.59.0] - 2023-11-27

Changed:

  * Change web API paths to avoid any potential URL segment clashes, #1136, OCR-D/spec#250
    * `GET /` -> `GET /info`
    * `POST /` -> `POST /run`
    * `/{job-id}` -> `/job/{job-id}`
    * `/{job-id}/log` -> `/log/{job-id}`

Fixed:

  * WorkspaceBagger: do not overwrite files in case of filename conflict, #1129, #1137
  * Update apidocs to include `ocrd_network`, #1131

Added:

  * `ocrd workspace update-page` to set attributes on the `mets:div` of a page, #1133, #1134
  * `ocrd workspace list-page` now has configurable output format and optional partitioning of the page list, #1140, #1141
  * `ocrd zip bag`, `ocrd workspace merge`, `ocrd workspace clone` now support whitelisting/blacklisting file groups, #356, #383, #506, #582, #1138, #1139
  * workflow endpoint supports storing and deduplicating workflows, #1143

Removed:

  * `OcrdMets`: remove Unused `__exit__` method,.#1130 #1132

## [2.58.1] - 2023-10-20

Fixed:

  * bashlib: regression introduced in v2.58.0 breaking non-mets-server calls, #1128

## [2.58.0] - 2023-10-20

Fixed:

  * `helpers.run_cli`: Handle both `int` and `str` log levels, #1121
  * bashlib: typo `ocrd_argv` -> `ocrd__argv`, #1122, #1123
  * <del>processing workers: pass log level as string and `initLogging` at the right time,</del> Handle logging of bashlib workers separately, #1123 #1127
  * `ocrd workspace bulk-add` now supports `-U/--mets-server-url`, #1126
  * bashlib: Support `-U` as alias for `--mets-server-url`, #1126

Added:

  * METS server: `POST /reload` to reload METS from disk, #1123, #1124

## [2.57.2] - 2023-10-18

Fixed:

  * bashlib: remove vestigial `--log-filename` option from #1105, #1120

## [2.57.1] - 2023-10-18

Fixed:

  * Docker deployment process, no functional change

## [2.57.0] - 2023-10-18

Fixed:

  * running a processor as a worker no longer dumps `ocrd-tool.json` and messed up logging, #1116

Changed:

  * logging: With `ocrd_logging.conf` (e.g. in Docker), log all messages `DEBUG` and up and log to `ocrd.log`, #1117

## [2.56.0] - 2023-10-13

Changed:

  * A separate logging dir tree structure for the modules (processing servers, processing workers, processor servers, mets servers, processing jobs). Configurable with env variable `OCRD_NETWORK_LOGS_ROOT_DIR`, #1111
    * Processing job-level logging - each job is logged into a separate file with format `{job_id}.log`
    * Processing job-level logging file paths are added to the Job models and preserved in the database.
    * The `ocrd_network` logging is based on the format provided in `ocrd_utils`
  * Support env variable `OCRD_NETWORK_SOCKETS_ROOT_DIR`  for setting the root directory for METS server sockets, #1111
  * An endpoint `/job/{id}/log` for getting the log file of a processing job of a processor, #1111

## [2.55.2] - 2023-10-12

Fixed:

  * `OcrdAgentModel`: `_type` must be `type`, pydantic/pydantic#6797, #1114

## [2.55.1] - 2023-10-12

Changed:

  * `ocrd workspace bulk-add` distinguishes between `url` and `local_filename`, supporting both, #1086, #1079, #1113

## [2.55.0] - 2023-10-11

Added:

  * `/workflow` endpoint that can handle `ocrd process` workflows and distribute jobs page-wise across workers, #1083, #1105, #1108, #1109

Changed:

  * METS Server: Make sockets world-readable and -writable, #1098, #1099
  * METS Server: Implement find_files support for `local_filename` and `url`, #1100
  * Logging: consistent logger names derived from `ocrd.`, #1101
  * Logging: consistent logging across the packages, including `ocrd_network`, #1101
  * `..` page range operator: allow single-page ranges, #1106, #1107

## [2.54.0] - 2023-09-12

Added:

  * METS Server: providing concurrent additional access to the METS file for parallel processing, #966
  * Web API: Cache jobs in the processing server with an optional callback once processed, #1069
  * Web API: Lock pages output file groups of a workspace to prevent simultaneous non-additive access to workspaces, #1069
  * Web API: Support job dependency for caching complete fully-deterministic workflows, #1069
  * Web API: Processing server will start all ready requests, not just the first one, #1069
  * Web API: Workers will create on demand, retry attempts configurable via `OCRD_NETWORK_WORKER_QUEUE_CONNECT_ATTEMPTS`, #1093
  * `ocrd_utils.config` to collect all configuration based on environment variables in one place, #1081
  * Processor CLI: Warn if a given page ID cannot be found in METS, #1088, #1089

Changed:

  * Processors now have `worker` and `server` subcommands, with separate --help, for starting processing worker/processor server, #1087
  * Move `tf_disable_interactive_logs` (to silence keras/tensorflow print statements) to `ocrd_utils.logging` and do not call on module-level, #1090, #1091
  * :fire: We do now properly distinguish between original and local-file FLocat, original URL will not be changed for downloads anymore, #323, #1079
  * :fire: logging has been streamlined to be better usable as a library, #1080

## [2.53.0] - 2023-08-21

Fixed:

  * `WorkspaceValidator`: make the check for consistency of `pc:Page[@pcGtsId]` and `mets:file[@ID]` optional with the `mets_fileid_page_pcgtsid` skip flag, #1066
  * `ocrd resmgr download`: use `basedir` as an arg and not a kwarg, #1078

Changed:

  * `WorkspaceValidator`: Download files temporarily/on-demand, #1066
  * `ocrd-* --version` now prints only the version of the processor without noise or core version, #1068

Added

  * Environment variables to control optional retries and timeouts for downloading files:
    * `OCRD_DOWNLOAD_RETRIES`: Number of times to retry failed attempts for downloads of workspace files. #1073
    * `OCRD_DOWNLOAD_TIMEOUT`: Timeout in seconds for connecting or reading (comma-separated) when downloading. #1073
  * Environment variables used throughout core are now documented in README and `ocrd --help`,  #1073
  * Web API: `--create-queue` option to on-demand create RabbitMQ for processing workers, #1075
  * Web API: `--queue-connec-attempts` to retry connection to RabbitMQ in case server is not yet running, #1075

## [2.52.0] - 2023-06-26

Added:

  * `make deps-cuda`: Makefile target to set up a working CUDA installation, both for native and Dockerfile.cuda, #1055
  * Implementation of the Standalone Processor Server module, #1030
  * `ocrd_utils.guess_media_type` to consistently try to determine media type from a file name, #1045

Changed:

  * Refactoring the Network CLI, all network module CLI are in `ocrd_network` now, #1030
  * The Processing Server uses [`ocrd-all-tool.json`](https://ocr-d.de/js/ocrd-all-tool.json) file, removing local processor install dependencies, #1030
  * Overall improvement and refactoring of the `ocrd_network` package, #1030
  * Optionally skip deployment of mongodb and rabbitmq to make external usage/management possible, #1048
  * `page_from_file` now also accepts a (`str`) file path in addition to `OcrdFile`, #1045
  * packaging: install/uninstall in correct build order, use `python -m build` instead of `python setup.py sdist bdist_wheel`, #1051

Removed:

  * Obsolete travis CI configuration removed, #1056
  * Support for end-of-life python versions 3.5 and 3.6, #1057

Fixed:

  * Makefile `FIND_VERSION` macro: use `grep -E` instead of `grep -P` for macos compatibility, #1060
  * `ocrd resmgr`: detect HTTP errors as such and don't try to continue if HTTP >= 400, #1062
  * `PageValidator`: Ensure TextLine has coordinates when checking for Baseline containment, #1049

## [2.51.0] - 2023-06-07

Changed:

  * `core cuda` Docker: CUDA base image working again, based on `ocrd/core` not `nvidia/cuda` in a separate `Dockerfile.cuda`, #1041
  * `core-cuda` Docker: adopt #1008 (venv under /usr/local, as in ocrd_all, instead of dist-packages), #1041
  * `core-cuda` Docker: use conda ([micromamba](https://mamba.readthedocs.io/en/latest/user_guide/micromamba.html)) for CUDA toolkit, and [nvidia-pyindex](https://pypi.org/project/nvidia-pyindex/) for CUDA libs – instead of [nvidia/cuda](https://hub.docker.com/r/nvidia/cuda) base image, #1041
  * more robust workaround for shapely#1598, #1041

Removed:

  * Revert #882 (fastentrypoints) as it enforces deps versions at runtime
  * Drop `ocrd_utils.package_resources` and use `pkg_resources.*` directly, #1041
  * `ocrd resmgr`: Drop redundant (processor-provided) entries in the central `resource_list.yml`.

## [2.50.0] - 2023-04-24

Added:

  * :fire: `ocrd_network`: Components related to OCR-D Web API, #974

Changed:

  * `bashlib`: support file input from multiple file groups, #1027, #1031

Fixed:

  * Don't output default docstrings for bashlib processors, #1026

## [2.49.0] - 2023-03-24

Changed:

  * :fire: (for now: also) publish Docker images to ghcr.io, not docker.io, #997
  * `ocrd resmgr`: eynollah models now provided by eynollah itself, qurator-spk/eynollah#91

## [2.48.1] - 2023-03-22

Changed:

  * `make docker-cuda`: Support CUDA 11.3 not 11.2, #1020

## [2.48.0] - 2023-03-22

Changed:

  * :fire: ocrd.run_processor / ocrd.processor.get_processor: rm unnecessary ocrd_tool kwarg #998, #1009
  * chdir into workspace directory for both cached and uncached `get_processor`, #972, 987
  * :fire: new CUDA base image 20.04, support CUDA runtime 11/12, not 10, #1014

Fixed:

  * `make install`: do not update opencv-python-headless or numpy for python `<= 3.6`, #1014

## [2.47.4] - 2023-03-16

Changed:

  * `resmgr`: `ocrd-typegroups-classifier` resources now listed decentrally, #1011, OCR-D/ocrd_typegroups_classifier#15

## [2.47.3] - 2023-03-15

Fixed:

  * Docker: reintroduce `python3-pip` because why not, #1004

## [2.47.2] - 2023-03-15

Fixed:

  * Docker: Use `pip3` not `pip`, #986
  * `make install`: Speed up opencv built for (now unsupported) python `<= 3.6`, #986, OCR-D/ocrd_calamari#72

Added:

  * CI/CD: GH action to deploy docker images to ghcr.io, #986

## [2.47.1] - 2023-03-15

Fixed:

  * Docker: install `python3-venv`, do not install `python3-pip`, #1003, #1004, OCR-D/ocrd_all#352

## [2.47.0] - 2023-03-15

Fixed:

  * `ocrd resmgr`: handle namespaces packages gracefully for Python `<=` 3.6, #917, #985
  * `ocrd resmgr`: guess media type with `filetype.py` in addition to `MIME_TO_EXT`, #991
  * `OcrdMets`: Insert `mets:agent` in a schema-compliant way, #976, #977
  * `ocrd_cli_wrap_processor`: remove unnecessary ocrd_tool kwarg, #998, #999
  * Docker base image builds again, except CUDA, #986

Added:

  * `ocrd resmgr`: support Google Drive links, #993, #992

Changed:

  * Use the new `importlib.resources.files` API, #995, #996
  * `ocrd resmgr`: resources for `ocrd_anybaseocr` removed from central list, provided by the project, #989, OCR-D/ocrd_anybaseocr#100

## [2.46.0] - 2023-02-16

Changed:

  * `WorkspaceValidator`: an `OcrdFile` without a pageId is not an error, but a document-wide file, #485, #979
  * `WorkspaceBackupManager`: add snapshot on init if enabled, #981
  * :fire: end-of-life for python 3.6, test from 3.7 to 3.11, #956
  * :fire: update base image to Ubuntu 20.04, #956

Fixed:

  * `bashlib`: Handle empty list of input files, #978
  * `OcrdMets.find_files`: don't override the `@LOCTYPE` of file candidates, #980
  * `ocrd resmgr`: replace libmagic with simple lookup by suffix, #982, #984

Added:

  * `helpers`: `get_cached_processor` to get instances of a processor in preparation for #974, #972

## [2.45.1] - 2023-01-20

Fixed:

  * `ocrd resmgr`: insert new entries first, so dedup works as expected, #971

## [2.45.0] - 2022-12-13

Fixed:

  * `ocrd resmgr download --overwrite` now works properly for both directories and files, #690, #797
  * `ocrd resmgr`: `archive` resources can now also be ZIP files and reference files and folders in them, #967
  * `ocrd-dummy`: can now be used to create PAGE-XML for images without copying, #803, #814

## [2.44.0] - 2022-12-08

Added:

  * `ocrd zip update` command to update checksums for an OCRD-ZIP after changing it, #363, #951

Removed:

  * `ocrd zip bag` does no longer support the long-broken `--in-place` option, #964, #363

## [2.43.0] - 2022-12-01

Added:

  * `OcrdMets.refresh_caches` to update caches after changes to XML outside of `OcrdMets`, #957, #960

## [2.42.1] - 2022-11-30

Fixed:

  * Regressions from PR #875, #957, #958
  * Missing import in `ocrd workspace merge`, #956

## [2.42.0] - 2022-11-23

Fixed:

  * Symlinks in workspaces are properly resolved now, #802, #954

Added:

  * Optional caching of access to METS, configured via [environment variable `OCRD_METS_CACHING`](https://github.com/OCR-D/core/#configuration), #875
  * CPU and memory profiling , configured via [environment variable `OCRD_PROFILE` and `OCRD_PROFILE_FILE`](https://github.com/OCR-D/core/#configuration), #678

Changed:

  * `ocrd workspace find`: supports comma-separated regexes, ranges and literal values for `--page-id`, #955
  * `ocrd workspace find`: ranges are generated with last number in string, #955


## [2.41.0] - 2022-11-09

Fixed:

  * `ocrd workspace list-installed` should not create spurious entries for `moduledir` files, #940
  * `OcrdResourceManager.download` does not need to query `size` via HTTP `Content-Length` in most cases, #924, #939
  * `make install`: Reinstall shapely to work around shapely/shapely#1598, #947

Changed:

  * `ocrd workspace bulk-add`: Generate file_id consistent with conventions from filename if no `--file-id` given, #943

## [2.40.0] - 2022-10-25

Fixed:

  * Downloading to `moduledir` should not create subdirectory, #934
  * Reduce logging noise in Ocrd{ResourceManager,Mets,Workspace}, #933, #916
  * Allow downloading resources explicitly to `module` location, #932

Changed:

  * bashlib processors support `--profile{-file}` and `--dump-module-dir`, #929

## [2.39.0] - 2022-10-23

Fixed:

  * `ocrd resmgr download '*'` working again, #904, #908, #909
  * Resource manager respects `moduledir` correctly, #904
  * `moduledir` now be able to handle namespace packages properly, #917
  * processing with `--overwrite` does not create duplicates any more, #861
  * bashlib: `ocrd validate tasks` call now supports non-standard METS name, #925

Added:

  * Processors have a `--dump-module-dir` to print their implementation-specific module directory to STDOUT, #904
  * `ocrd workspace merge`: support `--force` to overwrite mets:file with clashing IDs, #926

Changed:

  * `ocrd_utils.make_file_id`: only fall back to output fileGrp + (page)ID instead of page counter, #861
  * `OcrdWorkspace.add_file`: when ID already exists, remove (with overwrite) or fail instead of reusing
  * Workspace.merge: delegate `force` to each `add_file`

## [2.38.0] - 2022-08-14

Fixed:

  * `ocrd zip`: Properly respect `Ocrd-Mets`, #899
  * `ocrd workspace merge`: missing arguments, #896
  * `ocrd resmgr download`: Support dynamic discovery, #901

Added:

  * Processors support profiling with `--profile` and `--profile-file`, #878, bertsky/core#4

Removed:

  * `ocrd zip`: remove support for obsolete `Ocrd-Manifestation-Depth`, #902, OCR-D/spec#182

## [2.37.0] - 2022-08-03

Added:

  * `ocrd resmgr`: Resources of processors can be described in the `ocrd-tool.json`, #800

## [2.36.0] - 2022-07-18

Fixed:

  * `ocrd_utils.generate_range`: `maxsplits` should be 1, not 2, #880
  * Typos in CHANGELOG, README and code comments, #890

Changed:

  * Consistently use snake_case but continue to support CamelCase for kwargs and CLI options, #874, #862
  * Update to spec to 3.19.0, introducing greater flexibility in describing parameters, #872, #848, OCR-D/spec#206
  * `ocrd workspace merge`: support mapping `file_id` and `page_id` in addition to `file_grp`, #886, #888
  * `ocrd workspace merge`: rebase `OcrdFile.url` to target workspace, #887, #888
  * Replace `resource_filename` et al from pkg_resources with faster alternatives, #881, #882

## [2.35.0] - 2022-06-02

Changed:

  * OCRD-ZIP: Drop `Ocrd-Manifestation-Depth` and disallow `fetch.txt`, OCR-D/spec#182
  * Parameters can now be described with most JSON-Schema constructs, OCR-D/spec#206, #848

## [2.34.0] - 2022-05-20

Added:

  * `ocrd log` now accepts `-` argument to read messages from STDIN, #852, #870

Changed:

  * `ocrd_utils.safe_filename`: replace with `_` instead of `.` and retain pre-existing `_`, #858, #859
  * `OcrdMets.find_files`: allow pageId regex, precompile all regexes, #855, #856

Fixed:

  * `ocrd resmgr list-available`: handle processors not in resource list gracefully, #854, #865
  * `ocrd resmgr`: do not try to parse strings as dates, #867, #869
  * `ocrd workspace bulk-add`: use 1-based counter, #864

## [2.33.0] - 2022-05-03

Fixed:

  * `ocrd workspace remove-group`: Pass on `--recursive` to `remove_file_group`, #831, #832
  * `ocrd workspace bulk-add`: handle unset file_id properly, #812, #846
  * `io.BufferedReader` filename attribute should be `name` not `filename`, #838, #839

Changed:

  * `OcrdWorkspace.image_from_*`: support passing explicit AlternativeImage filename, #845

Removed:

  * `make asset-server` feature no longer used, #843
  * `python3-pip` dependency is redundant, #813

## [2.32.0] - 2022-03-30

Fixed:

  * `ocrd zip bag`: `-I` is *not* required, #828, #829

Changed:

  * `OcrdExif`: fallback to PIL if ImageMagick's `identify` is not available, #796, #676
  * `OcrdWorkspace.image_from_*`: Avoid false warning when recropping, #820, #687

## [2.31.0] - 2022-03-20

Changed:

  * `make cuda-ubuntu` installs all CUDA versions, OCR-D/core#704, OCR-D/ocrd_all#270
  * `ocrd resmgr`: updated models for ocrd-anybaseocr-{tiseg,layout-analysis}, #819, OCR-D/ocrd_anybaseocr#89

Fixed:

  * Error message erroneously referenced `mets:file/@ID` instead `mets:fileGrp/@USE`, #823
  * Consistently use kwargs/args in `OcrdWorkspace.save_image_file`, #822
  * Missing arg for log message in WorkspaceValidator, #811

## [2.30.0] - 2022-02-01

Changed:

  * Images processed by OCR-D can now be up to 40,000 by 40,000 pixels, #735, #768
  * `OcrdExif`: get pixel density metadata from ImageMagick's `identify`, not PIL, #676
  * Refactor parsing of `--mets`/`--mets-basename`/`--working-dir` to reduce ambiguities, #693, #696
  * bashlib: implify (i.e. remove) build process, #742, #785
  * `ocrd workspace bulk-add`: Make bulk-add more flexible and (hopefully) user-friendly, #641, #754, #769, #776

Fixed:

  * PAGE validation: handle `pc:ImageRegion` as well, #781
  * bashlib: pass on parameters for task validation, #784
  * `<processor> --list-resources`: List only the relevant type of resource (directory or file), #750, #777

## [2.29.0] - 2021-12-08

Changed:

  * `ocrd_utils.make_file_id`: combine with output fileGrp if input has pageId, but don't extract numbers, #744
  * `OcrdMets.add_file`: `mets:fileGrp/@USE` must be valid `xs:ID`, #746

Added:

  * `ocrd ocrd-tool`: wrap `list-resources` and `show-resource` from `Processor`
  * bashlib `ocrd__parse_argv`: add `--list-resources` and `--show-resource`, #751
  * `ocrd bashlib`: wrap `input-files` from `Processor` and `make_file_id`
  * bashlib `ocrd__wrap`: offer `ocrd__files` and `ocrd__input_file`, #571

## [2.28.0] - 2021-11-30

Added:

  * Store parameterization of processors in METS for provenance, #747
  * `ocrd workspace find --download`: Add a `--wait` option to wait between downloads, #745
  * bashlib: Check fileGrps when parsing CLI args, #743, OCR-D/ocrd_olena#76
  * Dockerfile: Install `time` to have `/usr/bin/time` in the image, #748, OCR-D/ocrd_all#271

Fixed:

  * `ocrd-dummy`: Also set pcGtsId, v0.0.2, #739

## [2.27.0] - 2021-11-09

Fixed:

  * remove dependency on six, #732
  * `ocrd workspace remove-group`: handle files not in subdir gracefully, #734
  * `ocrd resmgr`: fix "reference before assignment" issue #689, #733
  * `OcrdWorkspace.remove_file`: handle empty regexes, #725

Changed:

  * `ocrd workspace rename-group` will now also rename filenames and `mets:file/@ID`, #736

## [2.26.1] - 2021-10-14

Fixed:

  * `resmgr`: Correct URL for tesseract configs

## [2.26.0] - 2021-09-20

Added:

  * `ocrd_utils`: functions for scaling images, #707

Changed:

  * `OcrdFile`: should only ever be instantiated in the context of `OcrdMets`, #324, #714
  * Logging outputs to `STDERR` not `STDOUT`, OCR-D/spec#183, #713, #667

Fixed:

  * `ocrd workspace merge`: handle `file_grp` parameter, #715
  * `ocrd workspace merge`: explicit --copy-files was --no-copy-files, #715
  * `ocrd resmgr`: Fix tesseract URLs, #721

## [2.25.1] - 2021-06-30

Fixed:

  * `ocrd_page`: fallback for `id` if none of the attributes are set, #683

## [2.25.0] - 2021-06-30

Added:

  * `ocrd_page`: Universal attribute `id` to get either `id`, `imageFilename` or `pcGtsId`, #683, #682
  * `ocrd_page`: function `parseTree` and `with_etree` kwarg to `workspace.page_from_*` to access PAGE with etree API, #699, #313

Fixed:

  * Version-independent URL of METS XSD, #695, #694
  * Recrop if deskewed after cropping, #688

## [2.24.0] - 2021-04-27

Changed:

  * `workspace.image_from_page` will return the AlternativeImage with most features matched, not the last one, #686
  * `crop_image`: Ensures that masked areas do not influence the median for `fill='background'`, #686

## [2.23.3] - 2021-04-14

Added:

  * `ocrd resmgr`: model `default` for eynollah, #668

## [2.23.2] - 2021-03-10

Added:

  * `ocrd resmgr`: new model `default-2021-03-09` for sbb_binarization, #681

## [2.23.1] - 2021-03-07

Added:

  * `configs` resource for `ocrd-tesserocr-recognize`, #680

Changed:

  * Stop testing python 3.5, start testing python 3.9
  * `ocrd resmgr`: skip redundant `content-length` request if `size` is known

## [2.23.0] - 2021-02-26

Changed:

  * The `--page-id`/`-g` option now accepts value ranges with the `..` operator, #672

Added:

  * `ocrd workspace merge` to merge two workspaces, #670, #673
  * Two experimental calmari models `c1_fraktur19-1` and `c1_latin-script-hist-3`, #675

## [2.22.4] - 2021-02-17

Fixed:

  * `OcrdPage`: never output parsing results to STDOUT, #665, #372
  * improved docstrings throughout (ht @bertsky), #664
  * `resmgr --location cwd` will download to `$PWD`, not `$PWD/ocrd-resources/<executable>`, #671

## [2.22.3] - 2021-01-27

Changed:

  * resmgr: do not download on-demand when encountering unresolveable file parameters

Fixed:

  * resmgr: bugs in `--location cwd` resolving

## [2.22.2] - 2021-01-26

Changed:

  * resmgr/ocrd_calamari: disable pre-1.0 model
  * resmgr/ocrd_calamri: Rename resource `qurator-gt4hist{,ocr}-1.0`

## [2.22.1] - 2021-01-26

Fixed:

  * `mkdir -p $HOME/.config/ocrd`

## [2.22.0] - 2021-01-26

Added:

  * Implement file resource algorithm from OCR-D/spec#169, #559
  * New CLI `ocrd resmgr` to download/browse processor resources, #559
  * `Workspace.rename_file_group` with CLI `ocrd workspace rename-group` to rename file groups, #646
  * PAGE API method `get_AllTextLines`
  * resources for kraken

Changed:

  * `ocrd workspace add`: guess `--mimetype` if not provided, #658
  * `ocrd workspace add`: warn if `--page-id` not provided, #659

Fixed:
  * `run_cli`: don't reference undefined vars in error handler, #651
  * `name` of resources mustn't contain slash `/`

## [2.21.0] - 2020-11-27

Changed:

  * `prune_ReadingOrder`: also remove if RO contains only empty groups, #648
  * Don't restrict version range on `numpy`, #642
  * `run_cli`: measure both wall time and CPU time, #647

Fixed:

  * `TaskSequence.parse` do not hard-code class to instantiate, #649

## [2.20.2] - 2020-11-20

Fixed:

  * `ocrd workspace`: workspace directory should always be absolute, #644

## [2.20.1] - 2020-11-17

Fixed:

  * `Workspace.find_files`: Ignore `mets:file` w/o `mets:FLocat`, #640
  * Re-crop after rotation to avoid coordinate inconsistencies (and get tighter crops), #640
  * Handle missing `@orientation` by using the next-upper-level `@orientation`, #640

## [2.20.0] - 2020-11-03

Fixed:

  * Use `chmod`, not `fchmod` to support Windows, #636 ht @b2m
  * Do not capture processor output in `run_cli`, #592, #638

Changed:

  * Record version information in `pg:MetadataItem`, #637
  * New method `Processor.zip_input_files` to uniformly handle files from multiple input file groups, #635
  * Auto-invalidate derived `pg:AlternativeImage` images when changing coords, #639

## [2.19.0] - 2020-10-23

Changed:

  * CUDA base image is now nvidia/cuda:10.0-cudnn7-runtime-ubuntu18.04, #629 ht @Witiko
  * Convert 16-/32-bit images to 8-bit because PIL poorly supports the former, #627

Fixed:

  * Permission of existing `mets.xml` should not change, #403, #625
  * Handle `pg:AlternativeImage` without `comments`, #633

## [2.18.1] - 2020-10-21

Fixed:

  * default ocrd_logging.conf had a typo, #590, #628
  * default ocrd_logging.conf mirrors builtin logging config, #630
  * `--log-level` override mechanism works with logging config file, #626, #631

## [2.18.0] - 2020-10-12

Changed:

  * :fire: `OcrdMets.find_files` is now a generator, #614
  * Print docstrings if available for `--help`, #623
  * parameter values can be arrays, OCR-D/spec#174

## [2.17.2] - 2020-10-07

Fixed:

  * As a workaround for tensorflow compatibility, require `numpy < 1.19.0`, #620

## [2.17.1] - 2020-10-05

Fixed:

  * `ocrd workspace remove-group`: don't fail on non-existing files, #618

Changed:

  * media type <-> extension mapping for `text/plain`, #612

## [2.17.0] - 2020-09-23

Fixed:

  * `ocrd_utils.image` handles 16/32-bit images correctly, #606, python-pillow/Pillow#4925
  * OcrdPage: Most elements should be hashable, i.e. usable in sets, maps etc., #610
  * `ocrd_utils.make_file_id`: Ensure produced IDs are syntactically valid xs:ID, #616

Changed:

  * Calling a processor w/o any arguments: show help and exit 1, #586, #615
  * :fire: `Workspace.add_file` requires page_id kwarg (which can be None), #560
  * Reorganized the loggign to be more consistent and well-behaved, #599

## [2.16.3] - 2020-09-09

Fixed:

  * Prune empty reading order when serializing, #602

## [2.16.2] - 2020-09-08

Fixed:

  * handle empty reading order in PAGE gracefully, #600

## [2.16.1] - 2020-09-08

Fixed:

  * `ocrd_utils` on module-level, *disable* logging less than CRITICAL, call initLogging explicitly in CLI, #594

## [2.16.0] - 2020-09-03

Fixed:

  * `ocrd process`: better-readable output on failure, #583
  * `ocrd log` no longer produces "Logging errors" for multi-arg call, #588
  * `ocrd workspace remove-group`: remove empty file groups on disk, #584, #569

Added:

  * `METS_URL` can also be an OAI-PMH GetRecord request, ht @m3ssman, #581
  * Additional docker base image for Nvidia CUDA, ht @sepastian, #452

## [2.15.0] - 2020-08-28

Changed:

  * :fire: Finish deprecations on workspace CLI begun in 2.11.0, #578
    * `--mets-basename` is deprecated now, use `--mets` and `--directory`
    * Deprecated arguments are hidden in `--help`
    * some internal function name changes

## [2.14.0] - 2020-08-22

Fixed:

  * `make_file_id` ID incrementation algorithm failed under certain conditions, #570

Changed:

  * ValidationReport is now in ocrd_models, not ocrd_validators, #573
  * `run_cli` now returns `exitcode, stdout, stderr`, not just `exit_code`, #574
  * `ocrd-dummy` will create PAGE-XML for images on-the-fly, #574

Added:

  * processors can `self.add_metadata(pcgts)` to add a self-describing `pg:MetadataItem`, #574


## [2.13.2] - 2020-08-13

Fixed:

  * workspace: Possible source of "too many open files" closed, #564

## [2.13.1] - 2020-08-07

Changed:

  * `assert_file_grp_cardinality` accepts a third `msg` parameter

## [2.13.0] - 2020-08-04

Changed:

  * `Processor.input_files` can handle images mixed with PAGE-XML in a file group, OCR-D/spec#164, #554

## [2.12.7] - 2020-07-31

Changed:

  `ocrd process` also supports `-P`, #552

## [2.12.6] - 2020-07-28

Fixed:

  * Vulnerabilities in Pillow < 7.2.0, #550

## [2.12.5] - 2020-07-25

Changed:

  * `setOverrideLoglevel` now accepts a `silent` parameter, #548

Fixed:

  * No more logging output interfering with `--dump-json` et al. #540

## [2.12.4] - 2020-07-22

Fixed:

  * logging no longer interferes with `--dump-json`/`--help`/`--version`, #540, #546

## [2.12.3] - 2020-07-23

Fixed:

  * `ocrd workspace validate`: properly check whether AlternativeImage are available locally, #450, 543
  * `ocrd workspace validate`: reduce `INFO` log messages

## [2.12.2] - 2020-07-22

Fixed:

  * `ocrd_validators`: adapt ocrd-tool schema to include OCR-D/spec#152

## [2.12.1] - 2020-07-21

Fixed:

  * `ocrd process`: first task was ignored, #529, #542

## [2.12.0] - 2020-07-21

Changed:

  * Refactoring of `ocrd_utils.__init__` into thematic submodules, #536
  * validation of file groups downgraded to notice, allow PRE fileGrp/USE prefix, #541
  * BaseProcessor: :fire: show help if no METS was specified, OCR-D/spec#156, #438, #503

Fixed:

  * bashlib: Don't set `-x` in `ocrd__minversion`, #535
  * bashlib: `ocrd__minversion` logic was broken

## [2.11.0] - 2020-07-13

Fixed:

  * OcrdFile now has `__eq__` implementation to allow for `==`/`!=` comparisons, #532
  * `Workspace.image_from_page`: Respect the order of feature annotation on `page:AlternativeImage`, #525

Changed:

  * processors: `-p` is now repeatable and the referenced JSON may contain comments, #514, #533
  * `ocrd workspace validate`: `METS_URL` argument now optional as redundant to `--directory`/`--mets-basename`, #518
  * `ocrd workspace clone`: `WORKSPACE_DIR` argument now optional as redundant to `--directory`, #518
  * `ocrd workspace init`: `DIRECTORY` argument now optional as redundant to `--directory`, #518
  * `ocrd workpace *`: Pass `--mets-basename` on to resolver, #518

Added:

  * processors: `-P/--parameter-override` to override individual key-value pair of the parameter JSON, #533
  * utils: `make_file_id` to generate new `mets:file/@ID` from existing OcrdFiles, #530
  * utils: `assert_file_grp_cardinality` to assert the correct number of comma-separated fileGrps were passed, #530

## [2.10.5] - 2020-07-11

Fixed:

  * Blacklist PIL versions with PNG issues, #527
  * `ocrd workspace validate`: Allow skipping `page_xsd` and `mets_xsd`, #531
  * Fix import of `xlink` XSD in `mets` XSD, #531

## [2.10.4] - 2020-06-17

Added:

  * `bashlib`: support --overwrite flag, #522

## [2.10.3] - 2020-06-16

Fixed:

  * Regression in `ocrd workspace add` that prevented files from being copied, #519

## [2.10.2] - 2020-06-14

Fixed:

  * bashlib: Typo, #516

## [2.10.1] - 2020-06-13

Changed:
* bashlib: Make `input-file-grp` and `output-file-grp` mandatory, #512
* bashlib: Add a function `ocrd__minversion` that will check whether `ocrd --version` is new enough for the processor., #512

Fixed:

* Re-introduce `ocrd__raise`, #511
* Move XSD into root package of `ocrd_validators`, #513

## [2.10.0] - 2020-06-11

Fixed:

  * `--help`: Improve formatting of parameters, document `--overwrite`, ht @bersky

Changed:

  * `Workspace.remove_file`: Optional `page_recursive` parameter to remove images linked in PAGE as well, #434, #471
  * `Workspace.remove_file`: Optional `page_same_gropup` parameter to remove
    only those images linked in PAGE that are in the same group as the PAGE-XML
  * `Workspace.remove_file_gropup`: The same `page_recursive` and `page_same_gropup` parameters as `Workspace.remove_file`
  * `WorkspaceValidator.check_file_grp` now accepts a `page_id` parameter and will not raise an error if an existing
    output file group is targeted but for pages that aren't in that group, #471
  * `ocrd_cli_wrap_processor`: Take `page_id` into account when doing `WorkspaceValidator.check_file_grp`
  * `run_cli` accepts an `overwrite` parameter to pass on to processor calls, #471
  * <del>`Task.validate`: set implicit input/output groups from ocrd-tool.json, #471</del> blocked by OCR-D/spec#121
  * `ocrd process`: support --overwrite and pass on to processor calls, #471
  * `TaskSequencec.validate_tasks`: Check output file groups are not in METS unless overwrite for every task, ht @bersky
  * `ocrd workspace add` / `ocrd workspace bulk-add` support `--ignore`


Added:

  * Workspace: Optional `overwrite_mode` that sets `force` for all operations
  * `OcrdPage`: `get_AllAlternativeImagePaths` to list all `pc:AlternativeImage/@filename` referenced in a PcGts, #434, #471
  * `ocrd workspace bulk-add` to add many files at once to a workspace, #428
  * `OcrdMets.add_file`: `ignore` parameter to optionally disable looking for existing files, #428

## [2.9.0] - 2020-06-09

Changed:

  * `OcrdMets.add_file` now validates file ID syntax, #447

Added:

  * `ocrd log`, CLI to OCR-D's logging mechanism, #472
  * XML Schema validation of PAGE-XML and METS, #470

## [2.8.3] - 2020-06-08

Fixed:

  * workspace.remove_file: fix for list-valued results, #507


Changed:

  * workspace prune-files CLI: support filtering (like workspace find), #507
  * workspace CLI: update help strings (documenting regex support), #507


## [2.8.2] - 2020-06-08

Changed:

  * bashlib: check bash version to be >= 4.4, #445, OCR-D/ocrd_olena#30
  * `ocrd workspace add` supports `-C`/`--check-file-exists` to validate that `FNAME` is an existing local file, #495
  * `OcrdFile` constructor accepts `ID` parameter
  * `model_factory.page_from_image` now sets the `@pcGtsId` attribute tot the file's `@ID`, #378
  * `WorkspaceValidator`:  check `pc:PcGts/@pcGtsId` == `mets:file/@ID`, #378
  * `OcrdFile` constructor: removed long-obsolete `instance` parameter
  * `OcrdFile` constructor: accepts `pageId` parameter
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
  * incorporate changes to ocrd_tool schema from spec/v2.2.1

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
[3.0.0b5]: ../../compare/v3.0.0b5..v3.0.0b4
[3.0.0b4]: ../../compare/v3.0.0b4..v3.0.0b3
[3.0.0b3]: ../../compare/v3.0.0b3..v3.0.0b2
[3.0.0b2]: ../../compare/v3.0.0b2..v3.0.0b1
[3.0.0b1]: ../../compare/v3.0.0b1..v3.0.0a2
[3.0.0a2]: ../../compare/v3.0.0a2..v3.0.0a1
[3.0.0a1]: ../../compare/v3.0.0a1..v2.67.2
[2.70.0]: ../../compare/v2.70.0..v2.69.0
[2.69.0]: ../../compare/v2.69.0..v2.68.0
[2.68.0]: ../../compare/v2.68.0..v2.67.2
[2.67.2]: ../../compare/v2.67.2..v2.67.1
[2.67.1]: ../../compare/v2.67.1..v2.67.0
[2.67.0]: ../../compare/v2.67.0..v2.66.1
[2.66.1]: ../../compare/v2.66.1..v2.66.0
[2.66.0]: ../../compare/v2.66.0..v2.65.0
[2.65.0]: ../../compare/v2.65.0..v2.64.1
[2.64.1]: ../../compare/v2.64.1..v2.64.0
[2.64.0]: ../../compare/v2.63.0..v2.63.3
[2.63.3]: ../../compare/v2.63.3..v2.63.1
[2.63.2]: ../../compare/v2.63.2..v2.63.1
[2.63.1]: ../../compare/v2.63.1..v2.63.0
[2.63.0]: ../../compare/v2.63.0..v2.62.0
[2.62.0]: ../../compare/v2.62.0..v2.61.2
[2.61.2]: ../../compare/v2.61.2..v2.61.1
[2.61.1]: ../../compare/v2.61.1..v2.61.1
[2.61.0]: ../../compare/v2.61.0..v2.60.3
[2.60.3]: ../../compare/v2.60.3..v2.60.2
[2.60.2]: ../../compare/v2.60.2..v2.60.1
[2.60.1]: ../../compare/v2.60.1..v2.60.0
[2.60.0]: ../../compare/v2.60.0..v2.59.1
[2.59.1]: ../../compare/v2.59.1..v2.59.0
[2.59.0]: ../../compare/v2.59.0..v2.58.1
[2.58.0]: ../../compare/v2.58.1..v2.58.0
[2.58.0]: ../../compare/v2.58.0..v2.57.2
[2.57.2]: ../../compare/v2.57.2..v2.57.1
[2.57.1]: ../../compare/v2.57.1..v2.57.0
[2.57.0]: ../../compare/v2.57.0..v2.56.0
[2.56.0]: ../../compare/v2.56.0..v2.55.2
[2.55.2]: ../../compare/v2.55.2..v2.55.1
[2.55.1]: ../../compare/v2.55.1..v2.55.0
[2.55.0]: ../../compare/v2.55.0..v2.54.0
[2.54.0]: ../../compare/v2.54.0..v2.53.0
[2.53.0]: ../../compare/v2.53.0..v2.52.0
[2.52.0]: ../../compare/v2.52.0..v2.51.0
[2.51.0]: ../../compare/v2.51.0..v2.50.0
[2.50.0]: ../../compare/v2.50.0..v2.49.0
[2.49.0]: ../../compare/v2.49.0..v2.48.1
[2.48.1]: ../../compare/v2.48.1..v2.48.0
[2.48.0]: ../../compare/v2.48.0..v2.47.4
[2.47.4]: ../../compare/v2.47.4..v2.47.3
[2.47.3]: ../../compare/v2.47.3..v2.47.2
[2.47.2]: ../../compare/v2.47.2..v2.47.1
[2.47.1]: ../../compare/v2.47.1..v2.47.0
[2.47.0]: ../../compare/v2.47.0..v2.46.0
[2.46.0]: ../../compare/v2.46.0..v2.45.1
[2.45.1]: ../../compare/v2.45.1..v2.45.0
[2.45.0]: ../../compare/v2.45.0..v2.44.0
[2.44.0]: ../../compare/v2.44.0..v2.43.0
[2.43.0]: ../../compare/v2.43.0..v2.42.1
[2.42.1]: ../../compare/v2.42.1..v2.42.0
[2.42.0]: ../../compare/v2.42.0..v2.41.0
[2.41.0]: ../../compare/v2.41.0..v2.40.0
[2.40.0]: ../../compare/v2.40.0..v2.39.0
[2.39.0]: ../../compare/v2.39.0..v2.38.0
[2.38.0]: ../../compare/v2.38.0..v2.37.0
[2.37.0]: ../../compare/v2.37.0..v2.36.0
[2.36.0]: ../../compare/v2.36.0..v2.35.0
[2.35.0]: ../../compare/v2.35.0..v2.34.0
[2.34.0]: ../../compare/v2.34.0..v2.33.0
[2.33.0]: ../../compare/v2.33.0..v2.32.0
[2.32.0]: ../../compare/v2.32.0..v2.31.0
[2.31.0]: ../../compare/v2.31.0..v2.30.0
[2.30.0]: ../../compare/v2.30.0..v2.29.0
[2.29.0]: ../../compare/v2.29.0..v2.28.0
[2.28.0]: ../../compare/v2.28.0..v2.27.0
[2.27.0]: ../../compare/v2.27.0..v2.26.1
[2.26.1]: ../../compare/v2.26.1..v2.26.0
[2.26.0]: ../../compare/v2.26.0..v2.25.1
[2.25.1]: ../../compare/v2.25.1..v2.25.0
[2.25.0]: ../../compare/v2.25.0..v2.24.0
[2.24.0]: ../../compare/v2.24.0..v2.23.2
[2.23.2]: ../../compare/v2.23.2..v2.23.1
[2.23.1]: ../../compare/v2.23.1..v2.23.0
[2.23.0]: ../../compare/v2.23.0..v2.22.4
[2.22.4]: ../../compare/v2.22.4..v2.22.3
[2.22.3]: ../../compare/v2.22.3..v2.22.2
[2.22.2]: ../../compare/v2.22.2..v2.22.1
[2.22.1]: ../../compare/v2.22.1..v2.22.0
[2.22.0]: ../../compare/v2.22.0..v2.22.0b4
[2.22.0b4]: ../../compare/v2.22.0b4..v2.22.0b3
[2.22.0b3]: ../../compare/v2.22.0b3..v2.22.0b2
[2.22.0b2]: ../../compare/v2.22.0b2..v2.22.0b1
[2.22.0b1]: ../../compare/v2.22.0b1..v2.21.0
[2.21.0]: ../../compare/v2.21.0..v2.20.2
[2.20.2]: ../../compare/v2.20.2..v2.20.1
[2.20.1]: ../../compare/v2.20.1..v2.20.0
[2.20.0]: ../../compare/v2.20.0..v2.19.0
[2.19.0]: ../../compare/v2.19.0..v2.18.1
[2.18.1]: ../../compare/v2.18.1..v2.18.0
[2.18.0]: ../../compare/v2.18.0..v2.17.2
[2.17.2]: ../../compare/v2.17.2..v2.17.1
[2.17.1]: ../../compare/v2.17.1..v2.17.0
[2.17.0]: ../../compare/v2.17.0..v2.16.3
[2.16.3]: ../../compare/v2.16.3..v2.16.2
[2.16.2]: ../../compare/v2.16.2..v2.16.1
[2.16.1]: ../../compare/v2.16.1..v2.16.0
[2.16.0]: ../../compare/v2.16.0..v2.15.0
[2.15.0]: ../../compare/v2.15.0..v2.14.0
[2.14.0]: ../../compare/v2.14.0..v2.13.2
[2.13.2]: ../../compare/v2.13.2..v2.13.1
[2.13.1]: ../../compare/v2.13.1..v2.13.0
[2.13.0]: ../../compare/v2.13.0..v2.12.7
[2.12.7]: ../../compare/v2.12.7..v2.12.6
[2.12.6]: ../../compare/v2.12.6..v2.12.5
[2.12.5]: ../../compare/v2.12.5..v2.12.4
[2.12.4]: ../../compare/v2.12.4..v2.12.3
[2.12.3]: ../../compare/v2.12.3..v2.12.2
[2.12.2]: ../../compare/v2.12.2..v2.12.1
[2.12.1]: ../../compare/v2.12.1..v2.12.0
[2.12.0]: ../../compare/v2.12.0..v2.11.0
[2.11.0]: ../../compare/v2.11.0..v2.10.5
[2.10.5]: ../../compare/v2.10.5..v2.10.4
[2.10.4]: ../../compare/v2.10.4..v2.10.3
[2.10.3]: ../../compare/v2.10.3..v2.10.2
[2.10.2]: ../../compare/v2.10.2..v2.10.1
[2.10.1]: ../../compare/v2.10.1..v2.10.0
[2.10.0]: ../../compare/v2.10.0..v2.9.0
[2.9.0]: ../../compare/v2.9.0..v2.8.3
[2.8.3]: ../../compare/v2.8.3...v2.8.2
[2.8.2]: ../../compare/v2.8.2...v2.8.1
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
