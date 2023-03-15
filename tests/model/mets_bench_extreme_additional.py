# -*- coding: utf-8 -*-

from contextlib import contextmanager
from time import time

from pytest import main, fixture, mark

from ocrd import Resolver
from ocrd_utils import MIME_TO_EXT, getLogger
from ocrd_models import OcrdMets

logger = getLogger('ocrd.benchmark.mets')

GRPS_REG = ['SEG-REG', 'SEG-REPAIR', 'SEG-REG-DESKEW', 'SEG-REG-DESKEW-CLIP', 'SEG-LINE', 'SEG-REPAIR-LINE', 'SEG-LINE-RESEG-DEWARP']
GRPS_IMG = ['FULL', 'PRESENTATION', 'BIN', 'CROP', 'BIN2', 'BIN-DENOISE', 'BIN-DENOISE-DESKEW', 'OCR']

# 1500 files per page
REGIONS_PER_PAGE = 100
LINES_PER_REGION = 100
FILES_PER_PAGE = len(GRPS_IMG) * LINES_PER_REGION + len(GRPS_REG) * REGIONS_PER_PAGE

# Caching is disabled by default
def _build_mets(number_of_pages, force=False, cache_flag=False):
    mets = OcrdMets.empty_mets(cache_flag=cache_flag)
    mets._number_of_pages = number_of_pages

    for n in ['%04d' % (n + 1) for n in range(number_of_pages)]:
        _add_file = lambda n, fileGrp, mimetype, ID=None: mets.add_file(
            fileGrp,
            mimetype=mimetype,
            pageId='PHYS_%s' % n,
            ID=ID if ID else '%s_%s_%s' % (fileGrp, n, MIME_TO_EXT.get(mimetype)[1:].upper()),
            url='%s/%s%s' % (fileGrp, ID if ID else '%s_%s_%s' % (fileGrp, n, MIME_TO_EXT.get(mimetype)[1:].upper()), MIME_TO_EXT.get(mimetype))
        )
        for grp in GRPS_IMG:
            _add_file(n, grp, 'image/tiff')
            _add_file(n, grp, 'application/vnd.prima.page+xml')
        for grp in GRPS_REG:
            for region_n in range(REGIONS_PER_PAGE):
                _add_file(n, grp, 'image/png', '%s_%s_region%s' % (grp, n, region_n))

    return mets

def assert_len(expected_len, mets, kwargs):
    test_list = mets.find_all_files(**kwargs)
    assert expected_len == len(test_list)

def benchmark_find_files(number_of_pages, mets):
    benchmark_find_files_filegrp(number_of_pages, mets)
    benchmark_find_files_fileid(number_of_pages, mets)
    benchmark_find_files_physical_page(number_of_pages, mets)
    # This is not really useful to measure.
    # We iterate all files in both cached and non-cached in the same routine
    # When no specific search parameters are provided
    # benchmark_find_files_all(number_of_pages, mets)

def benchmark_find_files_filegrp(number_of_pages, mets):
	# Best case - first fileGrp
    assert_len((number_of_pages * REGIONS_PER_PAGE), mets, dict(fileGrp='SEG-REG'))
    # Worst case - does not exist
    assert_len(0, mets, dict(fileGrp='SEG-REG-NOTEXIST'))

def benchmark_find_files_fileid(number_of_pages, mets):
	# Best case - first file ID
    assert_len(1, mets, dict(ID='FULL_0001_TIF', fileGrp='FULL'))
    # Worst case - does not exist
    assert_len(0, mets, dict(ID='FULL_0001_TIF-NOTEXISTS', fileGrp='FULL-NOTEXIST'))

def benchmark_find_files_physical_page(number_of_pages, mets):
	# Best case - first physical page
    assert_len(FILES_PER_PAGE, mets, dict(pageId='PHYS_0001'))
    # Worst case - does not exist
    assert_len(0, mets, dict(pageId='PHYS_0001-NOTEXISTS'))

# Get all files, i.e., pass an empty search parameter -> dict()
def benchmark_find_files_all(number_of_pages, mets):
    assert_len((number_of_pages * FILES_PER_PAGE), mets, dict())

# ----- 500 pages -> build, search, build (cached), search (cached) ----- #
mets_500 = None
@mark.benchmark(group="build", max_time=0.1, min_rounds=1, disable_gc=False, warmup=False)
def test_b500(benchmark):
    @benchmark
    def result():
        global mets_500
        mets_500 = _build_mets(500, force=True)

@mark.benchmark(group="search", max_time=0.1, min_rounds=1, disable_gc=False, warmup=False)
def test_s500(benchmark):
    @benchmark
    def ret():
        global mets_500
        benchmark_find_files(500, mets_500)
del mets_500

mets_c_500 = None
@mark.benchmark(group="build_cached", max_time=0.1, min_rounds=1, disable_gc=False, warmup=False)
def test_b500_c(benchmark):
    @benchmark
    def result():
        global mets_c_500
        mets_c_500 = _build_mets(500, force=True, cache_flag=True)

@mark.benchmark(group="search_cached", max_time=0.1, min_rounds=1, disable_gc=False, warmup=False)
def test_s500_c(benchmark):
    @benchmark
    def ret():
        global mets_c_500
        benchmark_find_files(500, mets_c_500)
del mets_c_500

# ------------------------------------------------------------------------ #

if __name__ == '__main__':
    args = ['']
    # args.append('--benchmark-max-time=10')
    # args.append('--benchmark-min-time=0.1')
    # args.append('--benchmark-warmup=False')
    # args.append('--benchmark-disable-gc')
    args.append('--benchmark-verbose')
    args.append('--benchmark-min-rounds=1')
    args.append('--tb=short')
    main(args)
