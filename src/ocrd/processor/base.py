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
from typing import List, Optional, Union
import sys
import inspect
import tarfile
import io
from deprecated import deprecated

from ocrd.workspace import Workspace
from ocrd_models.ocrd_file import ClientSideOcrdFile, OcrdFile
from ocrd.processor.ocrd_page_result import OcrdPageResult
from ocrd_models.ocrd_page_generateds import PcGtsType
from ocrd_utils import (
    VERSION as OCRD_VERSION,
    MIMETYPE_PAGE,
    MIME_TO_EXT,
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
        self.message = "Could not find resource '%s' for executable '%s'. " \
                       "Try 'ocrd resmgr download %s %s' to download this resource." \
                       % (name, executable, executable, name)
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

    @property
    def metadata(self):
        """the ocrd-tool.json dict of the package"""
        if hasattr(self, '_metadata'):
            return self._metadata
        self._metadata = json.loads(resource_string(self.__module__.split('.')[0], 'ocrd-tool.json'))
        return self._metadata

    @property
    def version(self):
        """the version of the package"""
        if hasattr(self, '_version'):
            return self._version
        self._version = self.metadata['version']
        return self._version

    @property
    def executable(self):
        """the executable name of this processor tool"""
        if hasattr(self, '_executable'):
            return self._executable
        self._executable = os.path.basename(inspect.stack()[-1].filename)
        return self._executable

    @property
    def ocrd_tool(self):
        """the ocrd-tool.json dict of this processor tool"""
        if hasattr(self, '_ocrd_tool'):
            return self._ocrd_tool
        self._ocrd_tool = self.metadata['tools'][self.executable]
        return self._ocrd_tool

    def __init__(
            self,
            # FIXME: deprecate in favor of process_workspace(workspace)
            workspace : Optional[Workspace],
            ocrd_tool=None,
            parameter=None,
            input_file_grp=None,
            output_file_grp=None,
            page_id=None,
            download_files=True,
            version=None
    ):
        """
        Instantiate, but do not process. Unless ``list_resources`` or
        ``show_resource`` or ``show_help`` or ``show_version`` or
        ``dump_json`` or ``dump_module_dir`` is true, setup for processing
        (parsing and validating parameters, entering the workspace directory).

        Args:
             workspace (:py:class:`~ocrd.Workspace`): The workspace to process. \
                 Deprecated since version 3.0: Should be ``None`` here, but then needs to be set \
                 before processing.
        Keyword Args:
             parameter (string): JSON of the runtime choices for ocrd-tool ``parameters``. \
                 Can be ``None`` even for processing, but then needs to be set before running.
             input_file_grp (string): comma-separated list of METS ``fileGrp``s used for input. \
                 Deprecated since version 3.0: Should be ``None`` here, but then needs to be set \
                 before processing.
             output_file_grp (string): comma-separated list of METS ``fileGrp``s used for output. \
                 Deprecated since version 3.0: Should be ``None`` here, but then needs to be set \
                 before processing.
             page_id (string): comma-separated list of METS physical ``page`` IDs to process \
                 (or empty for all pages). \
                 Deprecated since version 3.0: Should be ``None`` here, but then needs to be set \
                 before processing.
             download_files (boolean): Whether input files will be downloaded prior to processing.
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
        if parameter is None:
            parameter = {}
        parameterValidator = ParameterValidator(self.ocrd_tool)

        report = parameterValidator.validate(parameter)
        if not report.is_valid:
            raise ValueError("Invalid parameters %s" % report.errors)
        self.parameter = parameter
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
        # FIXME: maybe we should enforce the cardinality properties to be specified or apply default=1 here
        # (but we already have ocrd-tool validation, and these first need to be adopted by implementors)
        if 'input_file_grp_cardinality' in self.ocrd_tool:
            assert_file_grp_cardinality(input_file_grps, self.ocrd_tool['input_file_grp_cardinality'],
                                        "Unexpected number of input file groups %d vs %s")
        if 'output_file_grp_cardinality' in self.ocrd_tool:
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

    @deprecated(version='3.0', reason='process() should be replaced with process_page() and process_workspace()')
    def process(self) -> None:
        """
        Process all files of the :py:attr:`workspace`
        from the given :py:attr:`input_file_grp`
        to the given :py:attr:`output_file_grp`
        for the given :py:attr:`page_id` (or all pages)
        under the given :py:attr:`parameter`.

        (This contains the main functionality and needs to be overridden by subclasses.)
        """
        raise NotImplementedError()

    def process_workspace(self, workspace: Workspace) -> None:
        """
        Process all files of the given ``workspace``,
        from the given :py:attr:`input_file_grp`
        to the given :py:attr:`output_file_grp`
        for the given :py:attr:`page_id` (or all pages)
        under the given :py:attr:`parameter`.

        (This will iterate over pages and files, calling
        :py:meth:`process_page`, handling exceptions.)
        """
        log = getLogger('ocrd.processor.base')
        with pushd_popd(workspace.directory):
            self.workspace = workspace
            self.verify()
            try:
                # FIXME: add page parallelization by running multiprocessing.Pool (#322)
                for input_file_tuple in self.zip_input_files(on_error='abort'):
                    # FIXME: add error handling by catching exceptions in various ways (#579)
                    # for example:
                    # - ResourceNotFoundError → use ResourceManager to download (once), then retry
                    # - transient (I/O or OOM) error → maybe sleep, retry
                    # - persistent (data) error → skip / dummy / raise
                    input_files : List[Optional[Union[OcrdFile, ClientSideOcrdFile]]] = [None] * len(input_file_tuple)
                    for i, input_file in enumerate(input_file_tuple):
                        if i == 0:
                            log.info("processing page %s", input_file.pageId)
                        elif input_file is None:
                            # file/page not found in this file grp
                            continue
                        input_files[i] = input_file
                        if not self.download:
                            continue
                        try:
                            input_files[i] = self.workspace.download_file(input_file)
                        except ValueError as e:
                            log.error(repr(e))
                            log.warning("skipping file %s for page %s", input_file, input_file.pageId)
                    self.process_page_file(*input_files)
            except NotImplementedError:
                # fall back to deprecated method
                self.process()

    def process_page_file(self, *input_files : Optional[Union[OcrdFile, ClientSideOcrdFile]]) -> None:
        """
        Process the given ``input_files`` of the :py:attr:`workspace`,
        representing one physical page (passed as one opened
        :py:class:`~ocrd_models.OcrdFile` per input fileGrp)
        under the given :py:attr:`parameter`, and make sure the
        results get added accordingly.

        (This uses process_page_pcgts, but can be overridden by subclasses
        to handle cases like multiple fileGrps, non-PAGE input etc.)
        """
        log = getLogger('ocrd.processor.base')
        input_pcgts : List[Optional[OcrdPage]] = [None] * len(input_files)
        assert isinstance(input_files[0], (OcrdFile, ClientSideOcrdFile))
        page_id = input_files[0].pageId
        for i, input_file in enumerate(input_files):
            assert isinstance(input_file, (OcrdFile, ClientSideOcrdFile))
            log.debug("parsing file %s for page %s", input_file.ID, input_file.pageId)
            try:
                page_ = page_from_file(input_file)
                assert isinstance(page_, PcGtsType)
                input_pcgts[i] = page_
            except ValueError as e:
                log.info("non-PAGE input for page %s: %s", page_id, e)
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
                file_path=image_file_path)
        result.pcgts.set_pcGtsId(output_file_id)
        self.add_metadata(result.pcgts)
        # FIXME: what about non-PAGE output like JSON ???
        self.workspace.add_file(file_id=output_file_id,
                                file_grp=self.output_file_grp,
                                page_id=page_id,
                                local_filename=os.path.join(self.output_file_grp, output_file_id + '.xml'),
                                mimetype=MIMETYPE_PAGE,
                                content=to_xml(result.pcgts))

    def process_page_pcgts(self, *input_pcgts : Optional[OcrdPage], page_id : Optional[str] = None) -> OcrdPageResult:
        """
        Process the given ``input_pcgts`` of the :py:attr:`workspace`,
        representing one physical page (passed as one parsed
        :py:class:`~ocrd_models.OcrdPage` per input fileGrp)
        under the given :py:attr:`parameter`, and return the
        resulting :py:class:`~ocrd.processor.OcrdPageResult`.

        Optionally, add to the ``images`` attribute of the resulting
        :py:class:`~ocrd.processor.OcrdPageResult` instances
        of :py:class:`~ocrd.processor.OcrdPageResultImage`,
        which have required fields for ``pil`` (:py:class:`PIL.Image` image data),
        ``file_id_suffix`` (used for generating IDs of the saved image) and
        ``alternative_image`` (reference of the :py:class:`ocrd_models.ocrd_page.AlternativeImageType`
        for setting the filename of the saved image).

        (This contains the main functionality and must be overridden by subclasses.)
        """
        raise NotImplementedError()

    def add_metadata(self, pcgts: OcrdPage) -> None:
        """
        Add PAGE-XML :py:class:`~ocrd_models.ocrd_page.MetadataItemType` ``MetadataItem`` describing
        the processing step and runtime parameters to :py:class:`~ocrd_models.ocrd_page.PcGtsType` ``pcgts``.
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
        https://ocr-d.de/en/spec/ocrd_tool#file-parameters

        Args:
            val (string): resource value to resolve
        """
        initLogging()
        executable = self.ocrd_tool['executable']
        log = getLogger('ocrd.processor.base')
        if exists(val):
            log.debug("Resolved to absolute path %s" % val)
            return val
        if hasattr(self, 'old_pwd'):
            cwd = self.old_pwd
        else:
            cwd = getcwd()
        ret = [cand for cand in list_resource_candidates(executable, val,
                                                         cwd=cwd, moduled=self.moduledir)
               if exists(cand)]
        if ret:
            log.debug("Resolved %s to absolute path %s" % (val, ret[0]))
            return ret[0]
        raise ResourceNotFoundError(val, executable)

    def show_resource(self, val):
        """
        Resolve a resource name to a file path with the algorithm in
        https://ocr-d.de/en/spec/ocrd_tool#file-parameters,
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
        Algorithm <https://github.com/cisocrgroup/ocrd_cis/pull/57#issuecomment-656336593>_

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
             mimetype (string): If not `None`, filter by the specified MIME
                 type (literal or regex prefixed by `//`). Otherwise prefer
                 PAGE or image.
        Returns:
            A list of :py:class:`ocrd_models.ocrd_file.OcrdFile` tuples.
        """
        if not self.input_file_grp:
            raise ValueError("Processor is missing input fileGrp")

        LOG = getLogger('ocrd.processor.base')
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
            # Warn if no files found but pageId was specified because that
            # might be because of invalid page_id (range)
            if self.page_id and not files_:
                msg = (f"Could not find any files for --page-id {self.page_id} - "
                       f"compare '{self.page_id}' with the output of 'orcd workspace list-page'.")
                if on_error == 'abort':
                    raise ValueError(msg)
                LOG.warning(msg)
            for file_ in files_:
                if not file_.pageId:
                    continue
                ift = pages.setdefault(file_.pageId, [None]*len(ifgs))
                if ift[i]:
                    LOG.debug("another file %s for page %s in input file group %s", file_.ID, file_.pageId, ifg)
                    # fileGrp has multiple files for this page ID
                    if mimetype:
                        # filter was active, this must not happen
                        if on_error == 'skip':
                            ift[i] = None
                        elif on_error == 'first':
                            pass # keep first match
                        elif on_error == 'last':
                            ift[i] = file_
                        elif on_error == 'abort':
                            raise ValueError(
                                "Multiple '%s' matches for page '%s' in fileGrp '%s'." % (
                                    mimetype, file_.pageId, ifg))
                        else:
                            raise Exception("Unknown 'on_error' strategy '%s'" % on_error)
                    elif (ift[i].mimetype == MIMETYPE_PAGE and
                          file_.mimetype != MIMETYPE_PAGE):
                        pass # keep PAGE match
                    elif (ift[i].mimetype == MIMETYPE_PAGE and
                          file_.mimetype == MIMETYPE_PAGE):
                        raise ValueError(
                            "Multiple PAGE-XML matches for page '%s' in fileGrp '%s'." % (
                                file_.pageId, ifg))
                    else:
                        # filter was inactive but no PAGE is in control, this must not happen
                        if on_error == 'skip':
                            ift[i] = None
                        elif on_error == 'first':
                            pass # keep first match
                        elif on_error == 'last':
                            ift[i] = file_
                        elif on_error == 'abort':
                            raise ValueError(
                                "No PAGE-XML for page '%s' in fileGrp '%s' but multiple matches." % (
                                    file_.pageId, ifg))
                        else:
                            raise Exception("Unknown 'on_error' strategy '%s'" % on_error)
                else:
                    LOG.debug("adding file %s for page %s to input file group %s", file_.ID, file_.pageId, ifg)
                    ift[i] = file_
        ifts = list()
        for page, ifiles in pages.items():
            for i, ifg in enumerate(ifgs):
                if not ifiles[i]:
                    # other fallback options?
                    LOG.error('found no page %s in file group %s',
                              page, ifg)
            if ifiles[0] or not require_first:
                ifts.append(tuple(ifiles))
        return ifts
