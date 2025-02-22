"""
Processor base class and helper functions.
"""

__all__ = [
    'Processor',
    'generate_processor_help',
    'run_cli',
    'run_processor'
]

from functools import cached_property
from os.path import exists, join
from shutil import copyfileobj
import json
import os
from os import getcwd
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, get_args
import sys
import logging
import logging.handlers
import inspect
import tarfile
import io
from collections import defaultdict
from frozendict import frozendict
# concurrent.futures is buggy in py38,
# this is where the fixes came from:
from loky import Future, ProcessPoolExecutor
import multiprocessing as mp
from threading import Timer
from _thread import interrupt_main

from click import wrap_text
from deprecated import deprecated
from requests import HTTPError

from ..workspace import Workspace
from ..mets_server import ClientSideOcrdMets
from ocrd_models.ocrd_file import OcrdFileType
from .ocrd_page_result import OcrdPageResult
from ocrd_utils import (
    VERSION as OCRD_VERSION,
    MIMETYPE_PAGE,
    MIME_TO_EXT,
    config,
    getLogger,
    list_resource_candidates,
    pushd_popd,
    list_all_resources,
    get_processor_resource_types,
    resource_filename,
    parse_json_file_with_comments,
    make_file_id,
    deprecation_warning
)
from ocrd_validators import ParameterValidator
from ocrd_models.ocrd_page import (
    PageType,
    AlternativeImageType,
    MetadataItemType,
    LabelType,
    LabelsType,
    OcrdPage,
    to_xml,
)
from ocrd_modelfactory import page_from_file
from ocrd_validators.ocrd_tool_validator import OcrdToolValidator

# XXX imports must remain for backwards-compatibility
from .helpers import run_cli, run_processor # pylint: disable=unused-import


class ResourceNotFoundError(FileNotFoundError):
    """
    An exception signifying the requested processor resource
    cannot be resolved.
    """
    def __init__(self, name, executable):
        self.name = name
        self.executable = executable
        self.message = (f"Could not find resource '{name}' for executable '{executable}'. "
                        f"Try 'ocrd resmgr download {executable} {name}' to download this resource.")
        super().__init__(self.message)

class NonUniqueInputFile(ValueError):
    """
    An exception signifying the specified fileGrp / pageId / mimetype
    selector yields multiple PAGE files, or no PAGE files but multiple images,
    or multiple files of that mimetype.
    """
    def __init__(self, fileGrp, pageId, mimetype):
        self.fileGrp = fileGrp
        self.pageId = pageId
        self.mimetype = mimetype
        self.message = (f"Could not determine unique input file for fileGrp {fileGrp} "
                        f"and pageId {pageId} under mimetype {mimetype or 'PAGE+image(s)'}")
        super().__init__(self.message)

class MissingInputFile(ValueError):
    """
    An exception signifying the specified fileGrp / pageId / mimetype
    selector yields no PAGE files, or no PAGE and no image files,
    or no files of that mimetype.
    """
    def __init__(self, fileGrp, pageId, mimetype):
        self.fileGrp = fileGrp
        self.pageId = pageId
        self.mimetype = mimetype
        self.message = (f"Could not find input file for fileGrp {fileGrp} "
                        f"and pageId {pageId} under mimetype {mimetype or 'PAGE+image(s)'}")
        super().__init__(self.message)

class DummyFuture:
    """
    Mimics some of `concurrent.futures.Future` but runs immediately.
    """
    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
    def result(self):
        return self.fn(*self.args, **self.kwargs)
class DummyExecutor:
    """
    Mimics some of `concurrent.futures.ProcessPoolExecutor` but runs
    everything immediately in this process.
    """
    def __init__(self, initializer=None, initargs=(), **kwargs):
        initializer(*initargs)
    def shutdown(self, **kwargs):
        # allow gc to catch processor instance (unless cached)
        _page_worker_set_ctxt(None, None)
    def submit(self, fn, *args, **kwargs) -> DummyFuture:
        return DummyFuture(fn, *args, **kwargs)

TFuture = Union[DummyFuture, Future]
TExecutor = Union[DummyExecutor, ProcessPoolExecutor]

class Processor():
    """
    A processor is a tool that implements the uniform OCR-D
    `command-line interface for run-time data processing <https://ocr-d.de/en/spec/cli>`_.

    That is, it executes a single workflow step, or a combination of workflow steps,
    on the workspace (represented by local METS). It reads input files for all or selected
    physical pages of the input fileGrp(s), computes additional annotation, and writes output
    files for them into the output fileGrp(s). It may take a number of optional or mandatory
    parameters.
    """

    max_instances : int = -1
    """
    maximum number of cached instances (ignored if negative), to be applied on top of
    :py:data:`~ocrd_utils.config.OCRD_MAX_PROCESSOR_CACHE` (i.e. whatever is smaller).

    (Override this if you know how many instances fit into memory - GPU / CPU RAM - at once.)
    """

    max_workers : int = -1
    """
    maximum number of processor forks for page-parallel processing (ignored if negative),
    to be applied on top of :py:data:`~ocrd_utils.config.OCRD_MAX_PARALLEL_PAGES` (i.e.
    whatever is smaller).

    (Override this if you know how many pages fit into processing units - GPU shaders / CPU cores
    - at once, or if your class already creates threads prior to forking, e.g. during ``setup``.)
    """

    max_page_seconds : int = -1
    """
    maximum number of seconds may be spent processing a single page (ignored if negative),
    to be applied on top of :py:data:`~ocrd_utils.config.OCRD_PROCESSING_PAGE_TIMEOUT`
    (i.e. whatever is smaller).

    (Override this if you know how costly this processor may be, irrespective of image size
    or complexity of the page.)
    """

    @property
    def metadata_filename(self) -> str:
        """
        Relative location of the ``ocrd-tool.json`` file inside the package.

        Used by :py:data:`metadata_location`.

        (Override if ``ocrd-tool.json`` is not in the root of the module,
        e.g. ``namespace/ocrd-tool.json`` or ``data/ocrd-tool.json``).
        """
        return 'ocrd-tool.json'

    @cached_property
    def metadata_location(self) -> Path:
        """
        Absolute path of the ``ocrd-tool.json`` file as distributed with the package.

        Used by :py:data:`metadata_rawdict`.

        (Override if ``ocrd-tool.json`` is not distributed with the Python package.)
        """
        module = inspect.getmodule(self)
        module_tokens = module.__package__.split('.')
        # for namespace packages, we cannot just use the first token
        for i in range(len(module_tokens)):
            prefix = '.'.join(module_tokens[:i + 1])
            if sys.modules[prefix].__spec__.has_location:
                return resource_filename(prefix, self.metadata_filename)
        raise Exception("cannot find top-level module prefix for %s", module.__package__)

    @cached_property
    def metadata_rawdict(self) -> dict:
        """
        Raw (unvalidated, unexpanded) ``ocrd-tool.json`` dict contents of the package.

        Used by :py:data:`metadata`.

        (Override if ``ocrd-tool.json`` is not in a file.)
        """
        return parse_json_file_with_comments(self.metadata_location)

    @cached_property
    def metadata(self) -> dict:
        """
        The ``ocrd-tool.json`` dict contents of the package, according to the OCR-D
        `spec <https://ocr-d.de/en/spec/ocrd_tool>`_ for processor tools.

        After deserialisation, it also gets validated against the
        `schema <https://ocr-d.de/en/spec/ocrd_tool#definition>`_ with all defaults
        expanded.

        Used by :py:data:`ocrd_tool` and :py:data:`version`.

        (Override if you want to provide metadata programmatically instead of a
        JSON file.)
        """
        metadata = self.metadata_rawdict
        report = OcrdToolValidator.validate(metadata)
        if not report.is_valid:
            self.logger.error(f"The ocrd-tool.json of this processor is {'problematic' if not report.errors else 'invalid'}:\n"
                              f"{report.to_xml()}.\nPlease open an issue at {metadata.get('git_url', 'the website')}.")
        return metadata

    @cached_property
    def version(self) -> str:
        """
        The program version of the package.
        Usually the ``version`` part of :py:data:`metadata`.

        (Override if you do not want to use :py:data:`metadata` lookup
        mechanism.)
        """
        return self.metadata['version']

    @cached_property
    def executable(self) -> str:
        """
        The executable name of this processor tool. Taken from the runtime
        filename.

        Used by :py:data:`ocrd_tool` for lookup in :py:data:`metadata`.

        (Override if your entry-point name deviates from the ``executable``
        name, or the processor gets instantiated from another runtime.)
        """
        return os.path.basename(inspect.stack()[-1].filename)

    @cached_property
    def ocrd_tool(self) -> dict:
        """
        The ``ocrd-tool.json`` dict contents of this processor tool.
        Usually the :py:data:`executable` key of the ``tools`` part
        of :py:data:`metadata`.

        (Override if you do not want to use :py:data:`metadata` lookup
        mechanism.)
        """
        return self.metadata['tools'][self.executable]

    @property
    def parameter(self) -> Optional[dict]:
        """the runtime parameter dict to be used by this processor"""
        if hasattr(self, '_parameter'):
            return self._parameter
        return None

    @parameter.setter
    def parameter(self, parameter : dict) -> None:
        if self.parameter is not None:
            self.shutdown()
        parameterValidator = ParameterValidator(self.ocrd_tool)
        report = parameterValidator.validate(parameter)
        if not report.is_valid:
            raise ValueError(f'Invalid parameters:\n{report.to_xml()}')
        # make parameter dict read-only
        self._parameter = frozendict(parameter)
        # (re-)run setup to load models etc
        self.setup()

    def __init__(
            self,
            # FIXME: remove in favor of process_workspace(workspace)
            workspace : Optional[Workspace],
            ocrd_tool=None,
            parameter=None,
            input_file_grp=None,
            output_file_grp=None,
            page_id=None,
            version=None
    ):
        """
        Instantiate, but do not setup (neither for processing nor other usage).
        If given, do parse and validate :py:data:`.parameter`.

        Args:
             workspace (:py:class:`~ocrd.Workspace`): The workspace to process. \
                 If not ``None``, then `chdir` to that directory.
                 Deprecated since version 3.0: Should be ``None`` here, but then needs to be set \
                 before processing.
        Keyword Args:
             parameter (string): JSON of the runtime choices for ocrd-tool ``parameters``. \
                 Can be ``None`` even for processing, but then needs to be set before running.
             input_file_grp (string): comma-separated list of METS ``fileGrp`` used for input. \
                 Deprecated since version 3.0: Should be ``None`` here, but then needs to be set \
                 before processing.
             output_file_grp (string): comma-separated list of METS ``fileGrp`` used for output. \
                 Deprecated since version 3.0: Should be ``None`` here, but then needs to be set \
                 before processing.
             page_id (string): comma-separated list of METS physical ``page`` IDs to process \
                 (or empty for all pages). \
                 Deprecated since version 3.0: Should be ``None`` here, but then needs to be set \
                 before processing.
        """
        if ocrd_tool is not None:
            deprecation_warning("Passing 'ocrd_tool' as keyword argument to Processor is deprecated - "
                                "use or override metadata/executable/ocrd-tool properties instead")
            self.ocrd_tool = ocrd_tool
            self.executable = ocrd_tool['executable']
        if version is not None:
            deprecation_warning("Passing 'version' as keyword argument to Processor is deprecated - "
                                "use or override metadata/version properties instead")
            self.version = version
        if workspace is not None:
            deprecation_warning("Passing a workspace argument other than 'None' to Processor "
                                "is deprecated - pass as argument to process_workspace instead")
            self.workspace = workspace
            self.old_pwd = getcwd()
            os.chdir(self.workspace.directory)
        if input_file_grp is not None:
            deprecation_warning("Passing an input_file_grp kwarg other than 'None' to Processor "
                                "is deprecated - pass as argument to process_workspace instead")
            self.input_file_grp = input_file_grp
        if output_file_grp is not None:
            deprecation_warning("Passing an output_file_grp kwarg other than 'None' to Processor "
                                "is deprecated - pass as argument to process_workspace instead")
            self.output_file_grp = output_file_grp
        if page_id is not None:
            deprecation_warning("Passing a page_id kwarg other than 'None' to Processor "
                                "is deprecated - pass as argument to process_workspace instead")
            self.page_id = page_id or None
        self.download = config.OCRD_DOWNLOAD_INPUT
        #: The logger to be used by processor implementations.
        # `ocrd.processor.base` internals should use :py:attr:`self._base_logger`
        self.logger = getLogger(f'ocrd.processor.{self.__class__.__name__}')
        self._base_logger = getLogger('ocrd.processor.base')
        if parameter is not None:
            self.parameter = parameter
        # workaround for deprecated#72 (@deprecated decorator does not work for subclasses):
        setattr(self, 'process',
                deprecated(version='3.0', reason='process() should be replaced with process_page_pcgts() or process_page_file() or process_workspace()')(getattr(self, 'process')))

    def __del__(self):
        self._base_logger.debug("shutting down %s in %s", repr(self), mp.current_process().name)
        self.shutdown()

    def show_help(self, subcommand=None):
        """
        Print a usage description including the standard CLI and all of this processor's ocrd-tool
        parameters and docstrings.
        """
        print(generate_processor_help(self.ocrd_tool, processor_instance=self, subcommand=subcommand))

    def show_version(self):
        """
        Print information on this processor's version and OCR-D version.
        """
        print("Version %s, ocrd/core %s" % (self.version, OCRD_VERSION))

    def verify(self):
        """
        Verify that :py:attr:`input_file_grp` and :py:attr:`output_file_grp` fulfill the processor's requirements.
        """
        # verify input and output file groups in parameters
        assert self.input_file_grp is not None
        assert self.output_file_grp is not None
        input_file_grps = self.input_file_grp.split(',')
        output_file_grps = self.output_file_grp.split(',')
        def assert_file_grp_cardinality(grps : List[str], spec : Union[int, List[int]], msg):
            if isinstance(spec, int):
                if spec > 0:
                    assert len(grps) == spec, msg % (len(grps), str(spec))
            else:
                assert isinstance(spec, list)
                minimum = spec[0]
                maximum = spec[1]
                if minimum > 0:
                    assert len(grps) >= minimum, msg % (len(grps), str(spec))
                if maximum > 0:
                    assert len(grps) <= maximum, msg % (len(grps), str(spec))
        # FIXME: enforce unconditionally as soon as grace period for deprecation is over
        if 'input_file_grp_cardinality' in self.ocrd_tool:
            assert_file_grp_cardinality(input_file_grps, self.ocrd_tool['input_file_grp_cardinality'],
                                        "Unexpected number of input file groups %d vs %s")
        if 'output_file_grp_cardinality' in self.ocrd_tool:
            assert_file_grp_cardinality(output_file_grps, self.ocrd_tool['output_file_grp_cardinality'],
                                        "Unexpected number of output file groups %d vs %s")
        # verify input and output file groups in METS
        for input_file_grp in input_file_grps:
            assert input_file_grp in self.workspace.mets.file_groups, \
                f"input fileGrp {input_file_grp} does not exist in workspace {self.workspace}"
        for output_file_grp in output_file_grps:
            assert output_file_grp not in self.workspace.mets.file_groups \
                or config.OCRD_EXISTING_OUTPUT in ['OVERWRITE', 'SKIP'] \
                or not any(self.workspace.mets.find_files(
                    pageId=self.page_id, fileGrp=output_file_grp)), \
                    f"output fileGrp {output_file_grp} already exists in workspace {self.workspace}"
        # keep this for backwards compatibility:
        return True

    def dump_json(self):
        """
        Print :py:attr:`ocrd_tool` on stdout.
        """
        print(json.dumps(self.ocrd_tool, indent=True))

    def dump_module_dir(self):
        """
        Print :py:attr:`moduledir` on stdout.
        """
        print(self.moduledir)

    def list_resources(self):
        """
        Find all installed resource files in the search paths and print their path names.
        """
        for res in self.list_all_resources():
            print(res)

    def setup(self) -> None:
        """
        Prepare the processor for actual data processing,
        prior to changing to the workspace directory but
        after parsing parameters.

        (Override this to load models into memory etc.)
        """
        pass

    def shutdown(self) -> None:
        """
        Bring down the processor after data processing,
        after to changing back from the workspace directory but
        before exiting (or setting up with different parameters).

        (Override this to unload models from memory etc.)
        """
        pass

    @deprecated(version='3.0', reason='process() should be replaced with process_page_pcgts() or process_page_file() or process_workspace()')
    def process(self) -> None:
        """
        Process all files of the :py:data:`workspace`
        from the given :py:data:`input_file_grp`
        to the given :py:data:`output_file_grp`
        for the given :py:data:`page_id` (or all pages)
        under the given :py:data:`parameter`.

        (This contains the main functionality and needs to be
        overridden by subclasses.)
        """
        raise NotImplementedError()

    def process_workspace(self, workspace: Workspace) -> None:
        """
        Process all files of the given ``workspace``,
        from the given :py:data:`input_file_grp`
        to the given :py:data:`output_file_grp`
        for the given :py:data:`page_id` (or all pages)
        under the given :py:data:`parameter`.

        Delegates to :py:meth:`.process_workspace_submit_tasks`
        and :py:meth:`.process_workspace_handle_tasks`.

        (This will iterate over pages and files, calling
        :py:meth:`.process_page_file` and handling exceptions.
        It should be overridden by subclasses to handle cases
        like post-processing or computation across pages.)
        """
        with pushd_popd(workspace.directory):
            self.workspace = workspace
            self.verify()
            try:
                # set up multitasking
                max_workers = max(0, config.OCRD_MAX_PARALLEL_PAGES)
                if self.max_workers > 0 and self.max_workers < config.OCRD_MAX_PARALLEL_PAGES:
                    self._base_logger.info("limiting number of workers from %d to %d", max_workers, self.max_workers)
                    max_workers = self.max_workers
                if max_workers > 1:
                    assert isinstance(workspace.mets, ClientSideOcrdMets), \
                        "OCRD_MAX_PARALLEL_PAGES>1 requires also using --mets-server-url"
                max_seconds = max(0, config.OCRD_PROCESSING_PAGE_TIMEOUT)
                if self.max_page_seconds > 0 and self.max_page_seconds < config.OCRD_PROCESSING_PAGE_TIMEOUT:
                    self._base_logger.info("limiting page timeout from %d to %d sec", max_seconds, self.max_page_seconds)
                    max_seconds = self.max_page_seconds

                if max_workers > 1:
                    executor_cls = ProcessPoolExecutor
                    log_queue = mp.get_context('fork').Queue()
                else:
                    executor_cls = DummyExecutor
                    log_queue = None
                executor = executor_cls(
                    max_workers=max_workers or 1,
                    # only forking method avoids pickling
                    context=mp.get_context('fork'),
                    # share processor instance as global to avoid pickling
                    initializer=_page_worker_set_ctxt,
                    initargs=(self, log_queue),
                )
                if max_workers > 1:
                    # forward messages from log queue (in subprocesses) to all root handlers
                    log_listener = logging.handlers.QueueListener(log_queue, *logging.root.handlers, respect_handler_level=True)
                    log_listener.start()
                tasks = None
                try:
                    self._base_logger.debug("started executor %s with %d workers", str(executor), max_workers or 1)
                    tasks = self.process_workspace_submit_tasks(executor, max_seconds)
                    stats = self.process_workspace_handle_tasks(tasks)
                finally:
                    executor.shutdown(kill_workers=True, wait=False)
                    self._base_logger.debug("stopped executor %s after %d tasks", str(executor), len(tasks) if tasks else -1)
                    if max_workers > 1:
                        # can cause deadlock:
                        #log_listener.stop()
                        # not much better:
                        #log_listener.enqueue_sentinel()
                        pass

            except NotImplementedError:
                # fall back to deprecated method
                try:
                    self.process()
                except Exception as err:
                    # suppress the NotImplementedError context
                    raise err from None

    def process_workspace_submit_tasks(self, executor : TExecutor, max_seconds : int) -> Dict[TFuture, Tuple[str, List[Optional[OcrdFileType]]]]:
        """
        Look up all input files of the given ``workspace``
        from the given :py:data:`input_file_grp`
        for the given :py:data:`page_id` (or all pages),
        and schedules calling :py:meth:`.process_page_file`
        on them for each page via `executor` (enforcing
        a per-page time limit of `max_seconds`).

        When running with `OCRD_MAX_PARALLEL_PAGES>1` and
        the workspace via METS Server, the executor will fork
        this many worker parallel subprocesses each processing
        one page at a time. (Interprocess communication is
        done via task and result queues.)

        Otherwise, tasks are run sequentially in the
        current process.

        Delegates to :py:meth:`.zip_input_files` to get 
        the input files for each page, and then calls
        :py:meth:`.process_workspace_submit_page_task`.

        Returns a dict mapping the per-page tasks
        (i.e. futures submitted to the executor)
        to their corresponding pageId and input files.
        """
        tasks = {}
        for input_file_tuple in self.zip_input_files(on_error='abort', require_first=False):
            task, page_id, input_files = self.process_workspace_submit_page_task(executor, max_seconds, input_file_tuple)
            tasks[task] = (page_id, input_files)
        self._base_logger.debug("submitted %d processing tasks", len(tasks))
        return tasks

    def process_workspace_submit_page_task(self, executor : TExecutor, max_seconds : int, input_file_tuple : List[Optional[OcrdFileType]]) -> Tuple[TFuture, str, List[Optional[OcrdFileType]]]:
        """
        Ensure all input files for a single page are
        downloaded to the workspace, then schedule
        :py:meth:`.process_process_file` to be run on
        them via `executor` (enforcing a per-page time
        limit of `max_seconds`).

        Delegates to :py:meth:`.process_page_file`
        (wrapped in :py:func:`_page_worker` to share
        the processor instance across forked processes).

        \b
        Returns a tuple of:
        - the scheduled future object,
        - the corresponding pageId,
        - the corresponding input files.
        """
        input_files : List[Optional[OcrdFileType]] = [None] * len(input_file_tuple)
        page_id = next(input_file.pageId
                       for input_file in input_file_tuple
                       if input_file)
        self._base_logger.info(f"preparing page {page_id}")
        for i, input_file in enumerate(input_file_tuple):
            if input_file is None:
                # file/page not found in this file grp
                continue
            input_files[i] = input_file
            if not self.download:
                continue
            try:
                input_files[i] = self.workspace.download_file(input_file)
            except (ValueError, FileNotFoundError, HTTPError) as e:
                self._base_logger.error(repr(e))
                self._base_logger.warning(f"failed downloading file {input_file} for page {page_id}")
        # process page
        #executor.submit(self.process_page_file, *input_files)
        return executor.submit(_page_worker, max_seconds, *input_files), page_id, input_files

    def process_workspace_handle_tasks(self, tasks : Dict[TFuture, Tuple[str, List[Optional[OcrdFileType]]]]) -> Tuple[int, int, Dict[str, int], int]:
        """
        Look up scheduled per-page futures one by one,
        handle errors (exceptions) and gather results.

        \b
        Enforces policies configured by the following
        environment variables:
        - `OCRD_EXISTING_OUTPUT` (abort/skip/overwrite)
        - `OCRD_MISSING_OUTPUT` (abort/skip/fallback-copy)
        - `OCRD_MAX_MISSING_OUTPUTS` (abort after all).

        \b
        Returns a tuple of:
        - the number of successfully processed pages
        - the number of failed (i.e. skipped or copied) pages
        - a dict of the type and corresponding number of exceptions seen
        - the number of total requested pages (i.e. success+fail+existing).

        Delegates to :py:meth:`.process_workspace_handle_page_task`
        for each page.
        """
        # aggregate info for logging:
        nr_succeeded = 0
        nr_failed = 0
        nr_errors = defaultdict(int) # count causes
        if config.OCRD_MISSING_OUTPUT == 'SKIP':
            reason = "skipped"
        elif config.OCRD_MISSING_OUTPUT == 'COPY':
            reason = "fallback-copied"
        for task in tasks:
            # wait for results, handle errors
            page_id, input_files = tasks[task]
            result = self.process_workspace_handle_page_task(page_id, input_files, task)
            if isinstance(result, Exception):
                nr_errors[result.__class__.__name__] += 1
                nr_failed += 1
                # FIXME: this is just prospective, because len(tasks)==nr_failed+nr_succeeded is not guaranteed
                if config.OCRD_MAX_MISSING_OUTPUTS > 0 and nr_failed / len(tasks) > config.OCRD_MAX_MISSING_OUTPUTS:
                    # already irredeemably many failures, stop short
                    nr_errors = dict(nr_errors)
                    raise Exception(f"too many failures with {reason} output ({nr_failed} of {nr_failed+nr_succeeded}, {str(nr_errors)})")
            elif result:
                nr_succeeded += 1
            # else skipped - already exists
        nr_errors = dict(nr_errors)
        nr_all = nr_succeeded + nr_failed
        if nr_failed > 0:
            if config.OCRD_MAX_MISSING_OUTPUTS > 0 and nr_failed / nr_all > config.OCRD_MAX_MISSING_OUTPUTS:
                raise Exception(f"too many failures with {reason} output ({nr_failed} of {nr_all}, {str(nr_errors)})")
            self._base_logger.warning("%s %d of %d pages due to %s", reason, nr_failed, nr_all, str(nr_errors))
        self._base_logger.debug("succeeded %d, missed %d of %d pages due to %s", nr_succeeded, nr_failed, nr_all, str(nr_errors))
        return nr_succeeded, nr_failed, nr_errors, len(tasks)

    def process_workspace_handle_page_task(self, page_id : str, input_files : List[Optional[OcrdFileType]], task : TFuture) -> Union[bool, Exception]:
        """
        \b
        Await a single page result and handle errors (exceptions), 
        enforcing policies configured by the following
        environment variables:
        - `OCRD_EXISTING_OUTPUT` (abort/skip/overwrite)
        - `OCRD_MISSING_OUTPUT` (abort/skip/fallback-copy)
        - `OCRD_MAX_MISSING_OUTPUTS` (abort after all).

        \b
        Returns
        - true in case of success
        - false in case the output already exists
        - the exception in case of failure
        """
        # FIXME: differentiate error cases in various ways:
        # - ResourceNotFoundError → use ResourceManager to download (once), then retry
        # - transient (I/O or OOM) error → maybe sleep, retry
        # - persistent (data) error → skip / dummy / raise
        try:
            self._base_logger.debug("waiting for output of task %s (page %s)", task, page_id)
            # timeout kwarg on future is useless: it only raises TimeoutError here,
            # but does not stop the running process/thread, and executor itself
            # offers nothing to that effect:
            # task.result(timeout=max_seconds or None)
            # so we instead applied the timeout within the worker function
            task.result()
            return True
        except NotImplementedError:
            # exclude NotImplementedError, so we can try process() below
            raise
        # handle input failures separately
        except FileExistsError as err:
            if config.OCRD_EXISTING_OUTPUT == 'ABORT':
                raise err
            if config.OCRD_EXISTING_OUTPUT == 'SKIP':
                return False
            if config.OCRD_EXISTING_OUTPUT == 'OVERWRITE':
                # too late here, must not happen
                raise Exception(f"got {err} despite OCRD_EXISTING_OUTPUT==OVERWRITE")
        except KeyboardInterrupt:
            raise
        # broad coverage of output failures (including TimeoutError)
        except Exception as err:
            # FIXME: add re-usable/actionable logging
            if config.OCRD_MISSING_OUTPUT == 'ABORT':
                self._base_logger.error(f"Failure on page {page_id}: {str(err) or err.__class__.__name__}")
                raise err
            self._base_logger.exception(f"Failure on page {page_id}: {str(err) or err.__class__.__name__}")
            if config.OCRD_MISSING_OUTPUT == 'SKIP':
                pass
            elif config.OCRD_MISSING_OUTPUT == 'COPY':
                self._copy_page_file(input_files[0])
            else:
                desc = config.describe('OCRD_MISSING_OUTPUT', wrap_text=False, indent_text=False)
                raise ValueError(f"unknown configuration value {config.OCRD_MISSING_OUTPUT} - {desc}")
            return err

    def _copy_page_file(self, input_file : OcrdFileType) -> None:
        """
        Copy the given ``input_file`` of the :py:data:`workspace`,
        representing one physical page (passed as one opened
        :py:class:`~ocrd_models.OcrdFile` per input fileGrp)
        and add it as if it was a processing result.
        """
        input_pcgts : OcrdPage
        assert isinstance(input_file, get_args(OcrdFileType))
        self._base_logger.debug(f"parsing file {input_file.ID} for page {input_file.pageId}")
        try:
            input_pcgts = page_from_file(input_file)
        except ValueError as err:
            # not PAGE and not an image to generate PAGE for
            self._base_logger.error(f"non-PAGE input for page {input_file.pageId}: {err}")
            return
        output_file_id = make_file_id(input_file, self.output_file_grp)
        input_pcgts.set_pcGtsId(output_file_id)
        self.add_metadata(input_pcgts)
        self.workspace.add_file(
            file_id=output_file_id,
            file_grp=self.output_file_grp,
            page_id=input_file.pageId,
            local_filename=os.path.join(self.output_file_grp, output_file_id + '.xml'),
            mimetype=MIMETYPE_PAGE,
            content=to_xml(input_pcgts),
        )

    def process_page_file(self, *input_files : Optional[OcrdFileType]) -> None:
        """
        Process the given ``input_files`` of the :py:data:`workspace`,
        representing one physical page (passed as one opened
        :py:class:`.OcrdFile` per input fileGrp)
        under the given :py:data:`.parameter`, and make sure the
        results get added accordingly.

        (This uses :py:meth:`.process_page_pcgts`, but should be overridden by subclasses
        to handle cases like multiple output fileGrps, non-PAGE input etc.)
        """
        input_pcgts : List[Optional[OcrdPage]] = [None] * len(input_files)
        assert isinstance(input_files[0], get_args(OcrdFileType))
        page_id = input_files[0].pageId
        self._base_logger.info("processing page %s", page_id)
        for i, input_file in enumerate(input_files):
            assert isinstance(input_file, get_args(OcrdFileType))
            self._base_logger.debug(f"parsing file {input_file.ID} for page {page_id}")
            try:
                page_ = page_from_file(input_file)
                assert isinstance(page_, OcrdPage)
                input_pcgts[i] = page_
            except ValueError as err:
                # not PAGE and not an image to generate PAGE for
                self._base_logger.error(f"non-PAGE input for page {page_id}: {err}")
        output_file_id = make_file_id(input_files[0], self.output_file_grp)
        output_file = next(self.workspace.mets.find_files(ID=output_file_id), None)
        if output_file and config.OCRD_EXISTING_OUTPUT != 'OVERWRITE':
            # short-cut avoiding useless computation:
            raise FileExistsError(
                f"A file with ID=={output_file_id} already exists {output_file} and neither force nor ignore are set"
            )
        result = self.process_page_pcgts(*input_pcgts, page_id=page_id)
        for image_result in result.images:
            image_file_id = f'{output_file_id}_{image_result.file_id_suffix}'
            image_file_path = join(self.output_file_grp, f'{image_file_id}.png')
            if isinstance(image_result.alternative_image, PageType):
                # special case: not an alternative image, but replacing the original image
                # (this is needed by certain processors when the original's coordinate system
                #  cannot or must not be kept)
                image_result.alternative_image.set_imageFilename(image_file_path)
                image_result.alternative_image.set_imageWidth(image_result.pil.width)
                image_result.alternative_image.set_imageHeight(image_result.pil.height)
            elif isinstance(image_result.alternative_image, AlternativeImageType):
                image_result.alternative_image.set_filename(image_file_path)
            elif image_result.alternative_image is None:
                pass # do not reference in PAGE result
            else:
                raise ValueError(f"process_page_pcgts returned an OcrdPageResultImage of unknown type "
                                 f"{type(image_result.alternative_image)}")
            self.workspace.save_image_file(
                image_result.pil,
                image_file_id,
                self.output_file_grp,
                page_id=page_id,
                file_path=image_file_path,
            )
        result.pcgts.set_pcGtsId(output_file_id)
        self.add_metadata(result.pcgts)
        self.workspace.add_file(
            file_id=output_file_id,
            file_grp=self.output_file_grp,
            page_id=page_id,
            local_filename=os.path.join(self.output_file_grp, output_file_id + '.xml'),
            mimetype=MIMETYPE_PAGE,
            content=to_xml(result.pcgts),
        )

    def process_page_pcgts(self, *input_pcgts : Optional[OcrdPage], page_id : Optional[str] = None) -> OcrdPageResult:
        """
        Process the given ``input_pcgts`` of the :py:data:`.workspace`,
        representing one physical page (passed as one parsed
        :py:class:`.OcrdPage` per input fileGrp)
        under the given :py:data:`.parameter`, and return the
        resulting :py:class:`.OcrdPageResult`.

        Optionally, add to the ``images`` attribute of the resulting
        :py:class:`.OcrdPageResult` instances of :py:class:`.OcrdPageResultImage`,
        which have required fields for ``pil`` (:py:class:`PIL.Image` image data),
        ``file_id_suffix`` (used for generating IDs of the saved image) and
        ``alternative_image`` (reference of the :py:class:`ocrd_models.ocrd_page.AlternativeImageType`
        for setting the filename of the saved image).

        (This contains the main functionality and must be overridden by subclasses,
        unless it does not get called by some overriden :py:meth:`.process_page_file`.)
        """
        raise NotImplementedError()

    def add_metadata(self, pcgts: OcrdPage) -> None:
        """
        Add PAGE-XML :py:class:`~ocrd_models.ocrd_page.MetadataItemType` ``MetadataItem`` describing
        the processing step and runtime parameters to :py:class:`.OcrdPage` ``pcgts``.
        """
        metadata_obj = pcgts.get_Metadata()
        assert metadata_obj is not None
        metadata_obj.add_MetadataItem(
                MetadataItemType(type_="processingStep",
                    name=self.ocrd_tool['steps'][0],
                    value=self.ocrd_tool['executable'],
                    Labels=[LabelsType(
                        externalModel="ocrd-tool",
                        externalId="parameters",
                        Label=[LabelType(type_=name,
                                         value=self.parameter[name])
                               for name in self.parameter.keys()]),
                            LabelsType(
                        externalModel="ocrd-tool",
                        externalId="version",
                        Label=[LabelType(type_=self.ocrd_tool['executable'],
                                         value=self.version),
                               LabelType(type_='ocrd/core',
                                         value=OCRD_VERSION)])
                    ]))

    def resolve_resource(self, val):
        """
        Resolve a resource name to an absolute file path with the algorithm in
        `spec <https://ocr-d.de/en/spec/ocrd_tool#file-parameters>`_

        Args:
            val (string): resource value to resolve
        """
        executable = self.ocrd_tool['executable']
        if exists(val):
            self._base_logger.debug("Resolved to absolute path %s" % val)
            return val
        # FIXME: remove once workspace arg / old_pwd is gone:
        if hasattr(self, 'old_pwd'):
            cwd = self.old_pwd
        else:
            cwd = getcwd()
        ret = [cand for cand in list_resource_candidates(executable, val,
                                                         cwd=cwd, moduled=self.moduledir)
               if exists(cand)]
        if ret:
            self._base_logger.debug("Resolved %s to absolute path %s" % (val, ret[0]))
            return ret[0]
        raise ResourceNotFoundError(val, executable)

    def show_resource(self, val):
        """
        Resolve a resource name to a file path with the algorithm in
        `spec <https://ocr-d.de/en/spec/ocrd_tool#file-parameters>`_,
        then print its contents to stdout.

        Args:
            val (string): resource value to show
        """
        res_fname = self.resolve_resource(val)
        fpath = Path(res_fname)
        if fpath.is_dir():
            with pushd_popd(fpath):
                fileobj = io.BytesIO()
                with tarfile.open(fileobj=fileobj, mode='w:gz') as tarball:
                    tarball.add('.')
                fileobj.seek(0)
                copyfileobj(fileobj, sys.stdout.buffer)
        else:
            sys.stdout.buffer.write(fpath.read_bytes())

    def list_all_resources(self):
        """
        List all resources found in the filesystem and matching content-type by filename suffix
        """
        mimetypes = get_processor_resource_types(None, self.ocrd_tool)
        for res in list_all_resources(self.ocrd_tool['executable'], moduled=self.moduledir):
            res = Path(res)
            if not '*/*' in mimetypes:
                if res.is_dir() and not 'text/directory' in mimetypes:
                    continue
                # if we do not know all MIME types, then keep the file, otherwise require suffix match
                if res.is_file() and not any(res.suffix == MIME_TO_EXT.get(mime, res.suffix)
                                             for mime in mimetypes):
                    continue
            yield res

    @property
    def module(self):
        """
        The top-level module this processor belongs to.
        """
        # find shortest prefix path that is not just a namespace package
        fqname = ''
        for name in self.__module__.split('.'):
            if fqname:
                fqname += '.'
            fqname += name
            if getattr(sys.modules[fqname], '__file__', None):
                return fqname
        # fall-back
        return self.__module__

    @property
    def moduledir(self):
        """
        The filesystem path of the module directory.
        """
        return resource_filename(self.module, '.')

    @property
    def input_files(self):
        """
        List the input files (for single-valued :py:attr:`input_file_grp`).

        For each physical page:

        - If there is a single PAGE-XML for the page, take it (and forget about all
          other files for that page)
        - Else if there is a single image file, take it (and forget about all other
          files for that page)
        - Otherwise raise an error (complaining that only PAGE-XML warrants
          having multiple images for a single page)

        See `algorithm <https://github.com/cisocrgroup/ocrd_cis/pull/57#issuecomment-656336593>`_

        Returns:
            A list of :py:class:`ocrd_models.ocrd_file.OcrdFile` objects.
        """
        if not self.input_file_grp:
            raise ValueError("Processor is missing input fileGrp")
        ret = self.zip_input_files(mimetype=None, on_error='abort')
        if not ret:
            return []
        assert len(ret[0]) == 1, 'Use zip_input_files() instead of input_files when processing multiple input fileGrps'
        return [tuples[0] for tuples in ret]

    def zip_input_files(self, require_first=True, mimetype=None, on_error='skip'):
        """
        List tuples of input files (for multi-valued :py:attr:`input_file_grp`).

        Processors that expect/need multiple input file groups,
        cannot use :py:data:`input_files`. They must align (zip) input files
        across pages. This includes the case where not all pages
        are equally present in all file groups. It also requires
        making a consistent selection if there are multiple files
        per page.

        Following the OCR-D functional model, this function tries to
        find a single PAGE file per page, or fall back to a single
        image file per page. In either case, multiple matches per page
        are an error (see error handling below).
        This default behaviour can be changed by using a fixed MIME
        type filter via :py:attr:`mimetype`. But still, multiple matching
        files per page are an error.

        Single-page multiple-file errors are handled according to
        :py:attr:`on_error`:

        - if ``skip``, then the page for the respective fileGrp will be
          silently skipped (as if there was no match at all)
        - if ``first``, then the first matching file for the page will be
          silently selected (as if the first was the only match)
        - if ``last``, then the last matching file for the page will be
          silently selected (as if the last was the only match)
        - if ``abort``, then an exception will be raised.

        Multiple matches for PAGE-XML will always raise an exception.

        Keyword Args:
             require_first (boolean): If true, then skip a page entirely
                 whenever it is not available in the first input `fileGrp`.
             on_error (string): How to handle multiple file matches per page.
             mimetype (string): If not `None`, filter by the specified MIME
                 type (literal or regex prefixed by `//`). Otherwise prefer
                 PAGE or image.
        Returns:
            A list of :py:class:`ocrd_models.ocrd_file.OcrdFile` tuples.
        """
        if not self.input_file_grp:
            raise ValueError("Processor is missing input fileGrp")

        ifgs = self.input_file_grp.split(",")
        # Iterating over all files repeatedly may seem inefficient at first sight,
        # but the unnecessary OcrdFile instantiations for posterior fileGrp filtering
        # can actually be much more costly than traversing the ltree.
        # This might depend on the number of pages vs number of fileGrps.

        pages = {}
        for i, ifg in enumerate(ifgs):
            files_ = sorted(self.workspace.mets.find_all_files(
                    pageId=self.page_id, fileGrp=ifg, mimetype=mimetype),
                                # sort by MIME type so PAGE comes before images
                                key=lambda file_: file_.mimetype)
            for file_ in files_:
                if not file_.pageId:
                    # ignore document-global files
                    continue
                ift = pages.setdefault(file_.pageId, [None]*len(ifgs))
                if ift[i]:
                    self._base_logger.debug(f"another file {file_.ID} for page {file_.pageId} in input file group {ifg}")
                    # fileGrp has multiple files for this page ID
                    if mimetype:
                        # filter was active, this must not happen
                        self._base_logger.warning(f"added file {file_.ID} for page {file_.pageId} in input file group {ifg} "
                                                  f"conflicts with file {ift[i].ID} of same MIME type {mimetype} - on_error={on_error}")
                        if on_error == 'skip':
                            ift[i] = None
                        elif on_error == 'first':
                            pass # keep first match
                        elif on_error == 'last':
                            ift[i] = file_
                        elif on_error == 'abort':
                            raise NonUniqueInputFile(ifg, file_.pageId, mimetype)
                        else:
                            raise Exception("Unknown 'on_error' strategy '%s'" % on_error)
                    elif (ift[i].mimetype == MIMETYPE_PAGE and
                          file_.mimetype != MIMETYPE_PAGE):
                        pass # keep PAGE match
                    elif (ift[i].mimetype == MIMETYPE_PAGE and
                          file_.mimetype == MIMETYPE_PAGE):
                        raise NonUniqueInputFile(ifg, file_.pageId, None)
                    else:
                        # filter was inactive but no PAGE is in control, this must not happen
                        self._base_logger.warning(f"added file {file_.ID} for page {file_.pageId} in input file group {ifg} "
                                                  f"conflicts with file {ift[i].ID} but no PAGE available - on_error={on_error}")
                        if on_error == 'skip':
                            ift[i] = None
                        elif on_error == 'first':
                            pass # keep first match
                        elif on_error == 'last':
                            ift[i] = file_
                        elif on_error == 'abort':
                            raise NonUniqueInputFile(ifg, file_.pageId, None)
                        else:
                            raise Exception("Unknown 'on_error' strategy '%s'" % on_error)
                else:
                    self._base_logger.debug(f"adding file {file_.ID} for page {file_.pageId} to input file group {ifg}")
                    ift[i] = file_
        # Warn if no files found but pageId was specified, because that might be due to invalid page_id (range)
        if self.page_id and not any(pages):
            self._base_logger.critical(f"Could not find any files for selected pageId {self.page_id}.\n"
                                       f"compare '{self.page_id}' with the output of 'orcd workspace list-page'.")
        ifts = []
        for page, ifiles in pages.items():
            for i, ifg in enumerate(ifgs):
                if not ifiles[i]:
                    # could be from non-unique with on_error=skip or from true gap
                    self._base_logger.error(f'Found no file for page {page} in file group {ifg}')
                    if config.OCRD_MISSING_INPUT == 'abort':
                        raise MissingInputFile(ifg, page, mimetype)
            if not any(ifiles):
                # must be from non-unique with on_error=skip
                self._base_logger.warning(f'Found no files for {page} - skipping')
                continue
            if ifiles[0] or not require_first:
                ifts.append(tuple(ifiles))
        return ifts

_page_worker_processor = None
"""
This global binding for the processor is required to avoid
squeezing the processor through a mp.Queue (which is impossible
due to unpicklable attributes like .workspace.mets._tree anyway)
when calling Processor.process_page_file as page worker processes
in Processor.process_workspace. Forking allows inheriting global
objects, and with the METS Server we do not mutate the local
processor instance anyway.
"""
def _page_worker_set_ctxt(processor, log_queue):
    """
    Overwrites `ocrd.processor.base._page_worker_processor` instance
    for sharing with subprocesses in ProcessPoolExecutor initializer.
    """
    global _page_worker_processor
    _page_worker_processor = processor
    if log_queue:
        # replace all log handlers with just one queue handler
        logging.root.handlers = [logging.handlers.QueueHandler(log_queue)]

def _page_worker(timeout, *input_files):
    """
    Wraps a `Processor.process_page_file` call as payload (call target)
    of the ProcessPoolExecutor workers, but also enforces the given timeout.
    """
    page_id = next((file.pageId for file in input_files
                    if hasattr(file, 'pageId')), "")
    if timeout > 0:
        timer = Timer(timeout, interrupt_main)
        timer.start()
    try:
        _page_worker_processor.process_page_file(*input_files)
        _page_worker_processor.logger.debug("page worker completed for page %s", page_id)
    except KeyboardInterrupt:
        _page_worker_processor.logger.debug("page worker timed out for page %s", page_id)
        raise TimeoutError()
    finally:
        if timeout > 0:
            timer.cancel()

def generate_processor_help(ocrd_tool, processor_instance=None, subcommand=None):
    """Generate a string describing the full CLI of this processor including params.

    Args:
         ocrd_tool (dict): this processor's ``tools`` section of the module's ``ocrd-tool.json``
         processor_instance (object, optional): the processor implementation
             (for adding any module/class/function docstrings)
        subcommand (string): 'worker' or 'server'
    """
    doc_help = ''
    if processor_instance:
        module = inspect.getmodule(processor_instance)
        if module and module.__doc__:
            doc_help += '\n' + inspect.cleandoc(module.__doc__) + '\n'
        if processor_instance.__doc__:
            doc_help += '\n' + inspect.cleandoc(processor_instance.__doc__) + '\n'
        # Try to find the most concrete docstring among the various methods that an implementation
        # could overload, first serving.
        # In doing so, compare with Processor to avoid a glitch in the way py>=3.5 inherits docstrings.
        # (They are supposed to only repeat information inspect.getdoc, rather than inherit __doc__ itself.)
        for method in ['process_page_pcgts', 'process_page_file', 'process_workspace', 'process']:
            instance_method = getattr(processor_instance, method)
            superclass_method = getattr(Processor, method)
            if instance_method.__doc__ and instance_method.__doc__ != superclass_method.__doc__:
                doc_help += '\n' + inspect.cleandoc(instance_method.__doc__) + '\n'
                break
        if doc_help:
            doc_help = '\n\n' + wrap_text(doc_help, width=72,
                                          initial_indent='  > ',
                                          subsequent_indent='  > ',
                                          preserve_paragraphs=True)
    subcommands = '''\
    worker      Start a processing worker rather than do local processing
    server      Start a processor server rather than do local processing
'''

    processing_worker_options = '''\
  --queue                         The RabbitMQ server address in format
                                  "amqp://{user}:{pass}@{host}:{port}/{vhost}"
                                  [amqp://admin:admin@localhost:5672]
  --database                      The MongoDB server address in format
                                  "mongodb://{host}:{port}"
                                  [mongodb://localhost:27018]
  --log-filename                  Filename to redirect STDOUT/STDERR to,
                                  if specified.
'''

    processing_server_options = '''\
  --address                       The Processor server address in format
                                  "{host}:{port}"
  --database                      The MongoDB server address in format
                                  "mongodb://{host}:{port}"
                                  [mongodb://localhost:27018]
'''

    processing_options = '''\
  -m, --mets URL-PATH             URL or file path of METS to process [./mets.xml]
  -w, --working-dir PATH          Working directory of local workspace [dirname(URL-PATH)]
  -I, --input-file-grp USE        File group(s) used as input
  -O, --output-file-grp USE       File group(s) used as output
  -g, --page-id ID                Physical page ID(s) to process instead of full document []
  --overwrite                     Remove existing output pages/images
                                  (with "--page-id", remove only those).
                                  Short-hand for OCRD_EXISTING_OUTPUT=OVERWRITE
  --debug                         Abort on any errors with full stack trace.
                                  Short-hand for OCRD_MISSING_OUTPUT=ABORT
  --profile                       Enable profiling
  --profile-file PROF-PATH        Write cProfile stats to PROF-PATH. Implies "--profile"
  -p, --parameter JSON-PATH       Parameters, either verbatim JSON string
                                  or JSON file path
  -P, --param-override KEY VAL    Override a single JSON object key-value pair,
                                  taking precedence over --parameter
  -U, --mets-server-url URL       URL of a METS Server for parallel incremental access to METS
                                  If URL starts with http:// start an HTTP server there,
                                  otherwise URL is a path to an on-demand-created unix socket
  -l, --log-level [OFF|ERROR|WARN|INFO|DEBUG|TRACE]
                                  Override log level globally [INFO]
  --log-filename LOG-PATH         File to redirect stderr logging to (overriding ocrd_logging.conf).
'''

    information_options = '''\
  -C, --show-resource RESNAME     Dump the content of processor resource RESNAME
  -L, --list-resources            List names of processor resources
  -J, --dump-json                 Dump tool description as JSON
  -D, --dump-module-dir           Show the 'module' resource location path for this processor
  -h, --help                      Show this message
  -V, --version                   Show version
'''

    parameter_help = ''
    if 'parameters' not in ocrd_tool or not ocrd_tool['parameters']:
        parameter_help = '  NONE\n'
    else:
        def wrap(s):
            return wrap_text(s, initial_indent=' '*3,
                             subsequent_indent=' '*4,
                             width=72, preserve_paragraphs=True)
        for param_name, param in ocrd_tool['parameters'].items():
            parameter_help += wrap('"%s" [%s%s]' % (
                param_name,
                param['type'],
                ' - REQUIRED' if 'required' in param and param['required'] else
                ' - %s' % json.dumps(param['default']) if 'default' in param else ''))
            parameter_help += '\n ' + wrap(param['description'])
            if 'enum' in param:
                parameter_help += '\n ' + wrap('Possible values: %s' % json.dumps(param['enum']))
            parameter_help += "\n"

    if not subcommand:
        return f'''\
Usage: {ocrd_tool['executable']} [worker|server] [OPTIONS]

  {ocrd_tool['description']}{doc_help}

Subcommands:
{subcommands}
Options for processing:
{processing_options}
Options for information:
{information_options}
Parameters:
{parameter_help}
'''
    elif subcommand == 'worker':
        return f'''\
Usage: {ocrd_tool['executable']} worker [OPTIONS]

  Run {ocrd_tool['executable']} as a processing worker.

  {ocrd_tool['description']}{doc_help}

Options:
{processing_worker_options}
'''
    elif subcommand == 'server':
        return f'''\
Usage: {ocrd_tool['executable']} server [OPTIONS]

  Run {ocrd_tool['executable']} as a processor sever.

  {ocrd_tool['description']}{doc_help}

Options:
{processing_server_options}
'''
    else:
        pass
