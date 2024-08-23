"""
Processor base class and helper functions.
"""

__all__ = [
    'Processor',
    'generate_processor_help',
    'run_cli',
    'run_processor'
]

from os.path import exists, join
from shutil import copyfileobj
import json
import os
from os import getcwd
from pathlib import Path
from typing import List, Optional, Union, get_args
import sys
import inspect
import tarfile
import io
import weakref
from warnings import warn
from frozendict import frozendict
from deprecated import deprecated
from requests import HTTPError

from ocrd.workspace import Workspace
from ocrd_models.ocrd_file import OcrdFileType
from ocrd.processor.ocrd_page_result import OcrdPageResult
from ocrd_utils import (
    VERSION as OCRD_VERSION,
    MIMETYPE_PAGE,
    MIME_TO_EXT,
    config,
    getLogger,
    initLogging,
    list_resource_candidates,
    pushd_popd,
    list_all_resources,
    get_processor_resource_types,
    resource_filename,
    resource_string,
    make_file_id,
    deprecation_warning
)
from ocrd_validators import ParameterValidator
from ocrd_models.ocrd_page import MetadataItemType, LabelType, LabelsType, OcrdPage, to_xml
from ocrd_modelfactory import page_from_file
from ocrd_validators.ocrd_tool_validator import OcrdToolValidator

# XXX imports must remain for backwards-compatibility
from .helpers import run_cli, run_processor, generate_processor_help # pylint: disable=unused-import


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

class Processor():
    """
    A processor is a tool that implements the uniform OCR-D command-line interface
    for run-time data processing. That is, it executes a single workflow step,
    or a combination of workflow steps, on the workspace (represented by local METS).
    It reads input files for all or requested physical pages of the input fileGrp(s),
    and writes output files for them into the output fileGrp(s). It may take 
    a number of optional or mandatory parameters.
    """

    max_instances : int = -1
    """
    maximum number of cached instances (ignored if negative), to be applied on top of
    :py:data:`~ocrd_utils.config.OCRD_MAX_PROCESSOR_CACHE` (i.e. whatever is smaller).

    (Override this if you know how many instances fit into memory at once.)
    """

    @property
    def metadata_location(self) -> str:
        """
        Location of `ocrd-tool.json` inside the package. By default we expect it in the root of the module
        """
        return 'ocrd-tool.json'

    @property
    def metadata(self) -> dict:
        """the ocrd-tool.json dict of the package"""
        if hasattr(self, '_metadata'):
            return self._metadata
        self._metadata = json.loads(resource_string(self.__module__.split('.')[0], self.metadata_location))
        report = OcrdToolValidator.validate(self._metadata)
        if not report.is_valid:
            self.logger.error(f"The ocrd-tool.json of this processor is {'problematic' if not report.errors else 'invalid'}:\n"
                              f"{report.to_xml()}.\nPlease open an issue at {self._metadata['git_url']}.")
        return self._metadata

    @property
    def version(self) -> str:
        """the version of the package"""
        if hasattr(self, '_version'):
            return self._version
        self._version = self.metadata['version']
        return self._version

    @property
    def executable(self) -> str:
        """the executable name of this processor tool"""
        if hasattr(self, '_executable'):
            return self._executable
        self._executable = os.path.basename(inspect.stack()[-1].filename)
        return self._executable

    @property
    def ocrd_tool(self) -> dict:
        """the ocrd-tool.json dict of this processor tool"""
        if hasattr(self, '_ocrd_tool'):
            return self._ocrd_tool
        self._ocrd_tool = self.metadata['tools'][self.executable]
        return self._ocrd_tool

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
            download_files=config.OCRD_DOWNLOAD_INPUT,
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
             download_files (boolean): Whether input files will be downloaded prior to processing, \
                 defaults to :py:attr:`ocrd_utils.config.OCRD_DOWNLOAD_INPUT` which is ``True`` by default
        """
        if ocrd_tool is not None:
            deprecation_warning("Passing 'ocrd_tool' as keyword argument to Processor is deprecated - "
                                "use or override metadata/executable/ocrd-tool properties instead")
            self._ocrd_tool = ocrd_tool
            self._executable = ocrd_tool['executable']
        if version is not None:
            deprecation_warning("Passing 'version' as keyword argument to Processor is deprecated - "
                                "use or override metadata/version properties instead")
            self._version = version
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
        self.download = download_files
        #: The logger to be used by processor implementations.
        # `ocrd.processor.base` internals should use :py:attr:`self._base_logger`
        self.logger = getLogger(f'ocrd.processor.{self.__class__.__name__}')
        self._base_logger = getLogger('ocrd.processor.base')
        if parameter is not None:
            self.parameter = parameter
        # ensure that shutdown gets called at destruction
        self._finalizer = weakref.finalize(self, self.shutdown)
        # workaround for deprecated#72 (@deprecated decorator does not work for subclasses):
        setattr(self, 'process',
                deprecated(version='3.0', reason='process() should be replaced with process_page() and process_workspace()')(getattr(self, 'process')))

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
        assert_file_grp_cardinality(input_file_grps, self.ocrd_tool['input_file_grp_cardinality'],
                                    "Unexpected number of input file groups %d vs %s")
        assert_file_grp_cardinality(output_file_grps, self.ocrd_tool['output_file_grp_cardinality'],
                                    "Unexpected number of output file groups %d vs %s")
        for input_file_grp in input_file_grps:
            assert input_file_grp in self.workspace.mets.file_groups
        # keep this for backwards compatibility:
        return True

    def dump_json(self):
        """
        Print :py:attr:`ocrd_tool` on stdout.
        """
        print(json.dumps(self.ocrd_tool, indent=True))
        return

    def dump_module_dir(self):
        """
        Print :py:attr:`moduledir` on stdout.
        """
        print(self.moduledir)
        return

    def list_resources(self):
        """
        Find all installed resource files in the search paths and print their path names.
        """
        for res in self.list_all_resources():
            print(res)
        return

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

        (This will iterate over pages and files, calling
        :py:meth:`.process_page_file` and handling exceptions.
        It should be overridden by subclasses to handle cases
        like post-processing or computation across pages.)
        """
        with pushd_popd(workspace.directory):
            self.workspace = workspace
            self.verify()
            try:
                # FIXME: add page parallelization by running multiprocessing.Pool (#322)
                for input_file_tuple in self.zip_input_files(on_error='abort', require_first=False):
                    input_files : List[Optional[OcrdFileType]] = [None] * len(input_file_tuple)
                    page_id = next(input_file.pageId
                                   for input_file in input_file_tuple
                                   if input_file)
                    self._base_logger.info(f"processing page {page_id}")
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
                    # FIXME: differentiate error cases in various ways:
                    # - ResourceNotFoundError → use ResourceManager to download (once), then retry
                    # - transient (I/O or OOM) error → maybe sleep, retry
                    # - persistent (data) error → skip / dummy / raise
                    try:
                        self.process_page_file(*input_files)
                    except Exception as err:
                        # we have to be broad here, but want to exclude NotImplementedError
                        if isinstance(err, NotImplementedError):
                            raise err
                        if isinstance(err, FileExistsError):
                            if config.OCRD_EXISTING_OUTPUT == 'ABORT':
                                raise err
                            if config.OCRD_EXISTING_OUTPUT == 'SKIP':
                                continue
                            if config.OCRD_EXISTING_OUTPUT == 'OVERWRITE':
                                # too late here, must not happen
                                raise Exception(f"got {err} despite OCRD_EXISTING_OUTPUT==OVERWRITE")
                        # FIXME: re-usable/actionable logging
                        self._base_logger.exception(f"Failure on page {page_id}: {err}")
                        if config.OCRD_MISSING_OUTPUT == 'ABORT':
                            raise err
                        if config.OCRD_MISSING_OUTPUT == 'SKIP':
                            continue
                        if config.OCRD_MISSING_OUTPUT == 'COPY':
                            self._copy_page_file(input_files[0])
                        else:
                            desc = config.describe('OCRD_MISSING_OUTPUT', wrap_text=False, indent_text=False)
                            raise ValueError(f"unknown configuration value {config.OCRD_MISSING_OUTPUT} - {desc}")
            except NotImplementedError:
                # fall back to deprecated method
                self.process()

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
        self.workspace.add_file(file_id=output_file_id,
                                file_grp=self.output_file_grp,
                                page_id=input_file.pageId,
                                local_filename=os.path.join(self.output_file_grp, output_file_id + '.xml'),
                                mimetype=MIMETYPE_PAGE,
                                content=to_xml(input_pcgts),
                                force=config.OCRD_EXISTING_OUTPUT == 'OVERWRITE',
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
        result = self.process_page_pcgts(*input_pcgts, page_id=page_id)
        for image_result in result.images:
            image_file_id = f'{output_file_id}_{image_result.file_id_suffix}'
            image_file_path = join(self.output_file_grp, f'{image_file_id}.png')
            image_result.alternative_image.set_filename(image_file_path)
            self.workspace.save_image_file(
                image_result.pil,
                image_file_id,
                self.output_file_grp,
                page_id=page_id,
                file_path=image_file_path,
                force=config.OCRD_EXISTING_OUTPUT == 'OVERWRITE',
            )
        result.pcgts.set_pcGtsId(output_file_id)
        self.add_metadata(result.pcgts)
        self.workspace.add_file(file_id=output_file_id,
                                file_grp=self.output_file_grp,
                                page_id=page_id,
                                local_filename=os.path.join(self.output_file_grp, output_file_id + '.xml'),
                                mimetype=MIMETYPE_PAGE,
                                content=to_xml(result.pcgts),
                                force=config.OCRD_EXISTING_OUTPUT == 'OVERWRITE',
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

        pages = dict()
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
        ifts = list()
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
