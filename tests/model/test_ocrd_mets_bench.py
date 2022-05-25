# -*- coding: utf-8 -*-

from contextlib import contextmanager
from time import time

from pytest import main, fixture, mark

from ocrd import Resolver
from ocrd_utils import MIME_TO_EXT, getLogger
from ocrd_models import OcrdMets

import pprint

# LOG = getLogger('ocrd.benchmark.mets')

GRPS_REG = ['SEG-REG', 'SEG-REPAIR', 'SEG-REG-DESKEW', 'SEG-REG-DESKEW-CLIP', 'SEG-LINE', 'SEG-REPAIR-LINE', 'SEG-LINE-RESEG-DEWARP']
GRPS_IMG = ['FULL', 'PRESENTATION', 'BIN', 'CROP', 'BIN2', 'BIN-DENOISE', 'BIN-DENOISE-DESKEW', 'OCR']

REGIONS_PER_PAGE = 10
LINES_PER_REGION = 2
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
            # LINES_PER_REGION = 2
            _add_file(n, grp, 'image/tiff')
            _add_file(n, grp, 'application/vnd.prima.page+xml')
        for grp in GRPS_REG:
            # REGIONS_PER_PAGE = 10
            for region_n in range(REGIONS_PER_PAGE):
                _add_file(n, grp, 'image/png', '%s_%s_region%s' % (grp, n, region_n))

    return mets

def assert_len(expected_len, mets, kwargs):
    test_list = mets.find_all_files(**kwargs)
    # print("kwargs: %s" % kwargs)
    # print("expected_len= %s, assert_len= %s" %(expected_len, len(test_list)))
    assert expected_len == len(test_list)

def benchmark_find_files(number_of_pages, mets):
    benchmark_find_files_filegrp(number_of_pages, mets)
    benchmark_find_files_fileid(number_of_pages, mets)
    #benchmark_find_files_all(number_of_pages, mets)

def benchmark_find_files_filegrp(number_of_pages, mets):
		# Best case - first fileGrp
        assert_len((number_of_pages * REGIONS_PER_PAGE), mets, dict(fileGrp='SEG-REG'))
        # Worst case - does not exist
        assert_len(0, mets, dict(fileGrp='SEG-REG-NOTEXIST'))

def benchmark_find_files_fileid(number_of_pages, mets):
		# Best case - first file ID
        assert_len(1, mets, dict(ID='FULL_0001_TIF'))
        # Worst case - does not exist
        assert_len(0, mets, dict(ID='FULL_0001_TIF-NOTEXISTS'))

# Get all files, i.e., pass an empty search parameter -> dict()
#def benchmark_find_files_all(number_of_pages, mets):
#        assert_len((number_of_pages * FILES_PER_PAGE), mets, dict())


# ----- METS files global variables ----- #
mets_5 = None
mets_10 = None
mets_20 = None
mets_50 = None

# ----- Build mets files with 5-10-20-50 pages ----- #
@mark.benchmark(group="build")
def test_b5(benchmark):
    @benchmark
    def result():
        global mets_5
        mets_5 = _build_mets(5, force=True)

@mark.benchmark(group="build")
def test_b10(benchmark):
    @benchmark
    def result():
        global mets_10
        mets_10 = _build_mets(10, force=True)

@mark.benchmark(group="build")
def test_b20(benchmark):
    @benchmark
    def result():
        global mets_20
        mets_20 = _build_mets(20, force=True)

@mark.benchmark(group="build")
def test_b50(benchmark):
    @benchmark
    def result():
        global mets_50
        mets_50 = _build_mets(50, force=True)

# ----- Search for files with 5-10-20-50 pages ----- #
@mark.benchmark(group="search")
def test_s5(benchmark):
    @benchmark
    def ret(): 
        global mets_5
        benchmark_find_files(5, mets_5)

@mark.benchmark(group="search")
def test_s10(benchmark):
    @benchmark
    def ret(): 
        global mets_10
        benchmark_find_files(10, mets_10)

@mark.benchmark(group="search")
def test_s20(benchmark):
    @benchmark
    def ret(): 
        global mets_20
        benchmark_find_files(20, mets_20)

@mark.benchmark(group="search")
def test_s50(benchmark):
    @benchmark
    def ret(): 
        global mets_50
        benchmark_find_files(50, mets_50)

del mets_5
del mets_10
del mets_20
del mets_50



# ----- METS files (cached) global variables ----- #
mets_c_5 = None
mets_c_10 = None
mets_c_20 = None
mets_c_50 = None

# ----- Build mets files (cached) with 5-10-20-50 pages ----- #
@mark.benchmark(group="build")
def test_b5_c(benchmark):
    @benchmark
    def result():
        global mets_c_5
        mets_c_5 = _build_mets(5, force=True, cache_flag=True)

@mark.benchmark(group="build")
def test_b10_c(benchmark):
    @benchmark
    def result():
        global mets_c_10
        mets_c_10 = _build_mets(10, force=True, cache_flag=True)

@mark.benchmark(group="build")
def test_b20_c(benchmark):
    @benchmark
    def result():
        global mets_c_20
        mets_c_20 = _build_mets(20, force=True, cache_flag=True)

@mark.benchmark(group="build")
def test_b50_c(benchmark):
    @benchmark
    def result():
        global mets_c_50
        mets_c_50 = _build_mets(50, force=True, cache_flag=True)

# ----- Search for files (cached) with 5-10-20-50 pages ----- #
@mark.benchmark(group="search")
def test_s5_c(benchmark):
    @benchmark
    def ret():
        global mets_c_5
        benchmark_find_files(5, mets_c_5)

@mark.benchmark(group="search")
def test_s10_c(benchmark):
    @benchmark
    def ret(): 
        global mets_c_10
        benchmark_find_files(10, mets_c_10)

@mark.benchmark(group="search")
def test_s20_c(benchmark):
    @benchmark
    def ret(): 
        global mets_c_20
        benchmark_find_files(20, mets_c_20)

@mark.benchmark(group="search")
def test_s50_c(benchmark):
    @benchmark
    def ret(): 
        global mets_c_50
        benchmark_find_files(50, mets_c_50)

del mets_c_5
del mets_c_10
del mets_c_20
del mets_c_50

def manual_t():
    mets = _build_mets(2, cache_flag=False)
    mets_cached = _build_mets(2, cache_flag=True)    

    # print("METS>--------------------------------------------------------------------")
    # print(mets)
    # print("-------------------------------------------------------------------------")
    # print("METS_cached>-------------------------------------------------------------")
    # print(mets_cached)

    print("-----Regular-Bench------------------------------------------------------------")
    benchmark_find_files(2, mets)
    print("-----Cached-Bench-------------------------------------------------------------")
    benchmark_find_files(2, mets_cached)
    
    print("-----Regular------------------------------------------------------------------")
    print("len=%d" % len(mets.find_all_files(fileGrp='SEG-REG')))
    print(mets.find_all_files(fileGrp='SEG-REG'))
    
    print("-----Cached-------------------------------------------------------------------")
    print("len=%d" % len(mets_cached.find_all_files(fileGrp='SEG-REG')))
    print(mets_cached.find_all_files(fileGrp='SEG-REG'))

if __name__ == '__main__':
    args = ['']
    # args.append('--benchmark-max-time=10')
    # args.append('--benchmark-min-time=0.1')
    # args.append('--benchmark-warmup=True')
    # args.append('--benchmark-disable-gc')
    args.append('--benchmark-verbose')
    args.append('--benchmark-min-rounds=1')
    args.append('--tb=short')
    main(args)
	
    # This function was used to manually test things
    # manual_t()
