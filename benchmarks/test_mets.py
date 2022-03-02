from contextlib import contextmanager
from time import time

from pytest import main, fixture, mark

from ocrd import Resolver
from ocrd_utils import MIME_TO_EXT, getLogger
from ocrd_models import OcrdMets

import pprint

from test_mets2 import build_mets2

LOG = getLogger('ocrd.benchmark.mets')

GRPS_REG = ['SEG-REG', 'SEG-REPAIR', 'SEG-REG-DESKEW', 'SEG-REG-DESKEW-CLIP', 'SEG-LINE', 'SEG-REPAIR-LINE', 'SEG-LINE-RESEG-DEWARP']
GRPS_IMG = ['FULL', 'PRESENTATION', 'BIN', 'CROP', 'BIN2', 'BIN-DENOISE', 'BIN-DENOISE-DESKEW', 'OCR']

REGIONS_PER_PAGE = 10
LINES_PER_REGION = 2
FILES_PER_PAGE = len(GRPS_IMG) * LINES_PER_REGION + len(GRPS_REG) * REGIONS_PER_PAGE

# Builder for mets with OcrdMets class
def _build_mets(number_of_pages, force=False):
    mets = OcrdMets.empty_mets()
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

#@contextmanager
#def generated_mets(number_of_pages):
#    mets = _build_mets(number_of_pages)
#    yield mets

def assert_len(expected_len, mets, kwargs):
    test_list = mets.find_all_files(**kwargs)
    # print("expected_len= %s, assert_len= %s" %(expected_len, len(test_list)))
    assert expected_len == len(test_list)

def assert_len2(expected_len2, mets2, kwargs):
    test_list2 = mets2.mm_find_all_files(**kwargs)
    # print("expected_len2= %s, assert_len2= %s" %(expected_len2, len(test_list2)))
    assert expected_len2 == len(test_list2)

def benchmark_find_files(number_of_pages, mets):
    benchmark_find_files_filegrp(number_of_pages, mets)
    benchmark_find_files_pageid(number_of_pages, mets)
    benchmark_find_files_all(number_of_pages, mets)

def benchmark_find_files_filegrp(number_of_pages, mets):
        assert_len((number_of_pages * REGIONS_PER_PAGE), mets, dict(fileGrp='SEG-REG'))
        assert_len(0, mets, dict(fileGrp='SEG-REG-NOTEXIST'))

def benchmark_find_files_pageid(number_of_pages, mets):
        # print(mets.find_all_files()[0].pageId)
        assert_len(FILES_PER_PAGE, mets, dict(pageId='PHYS_0001'))

# Get all files, i.e., pass an empty search parameter -> dict()
def benchmark_find_files_all(number_of_pages, mets):
        assert_len((number_of_pages * FILES_PER_PAGE), mets, dict())



def benchmark_find_files2(number_of_pages, mets2):
    benchmark_find_files_filegrp2(number_of_pages, mets2)
    benchmark_find_files_pageid2(number_of_pages, mets2)
    benchmark_find_files_all2(number_of_pages, mets2)

def benchmark_find_files_filegrp2(number_of_pages, mets2):
        assert_len2((number_of_pages * REGIONS_PER_PAGE), mets2, dict(fileGrp='SEG-REG'))
        assert_len2(0, mets2, dict(fileGrp='SEG-REG-NOTEXIST'))

def benchmark_find_files_pageid2(number_of_pages, mets2):
        # print(mets2.mm_find_all_files()[0].pageId)
        assert_len2(FILES_PER_PAGE, mets2, dict(pageId='PHYS_0001'))

# Get all files, i.e., pass an empty search parameter -> dict()
def benchmark_find_files_all2(number_of_pages, mets2):
        assert_len2((number_of_pages * FILES_PER_PAGE), mets2, dict())


#def benchmark_find_files_exclude(number_of_pages):
#    with generated_mets(number_of_pages) as (mets, assert_len):
#        print(mets.find_all_files()[0].pageId)
#        assert_len(dict(pageId_exclude='PHYS_0001'), (number_of_pages - 1) * FILES_PER_PAGE)
    # def test_find_files(self):
    #     self.assertEqual(len(self.mets.find_all_files()), 35, '35 files total')
    #     self.assertEqual(len(self.mets.find_all_files(fileGrp='OCR-D-IMG')), 3, '3 files in "OCR-D-IMG"')
    #     self.assertEqual(len(self.mets.find_all_files(fileGrp='//OCR-D-I.*')), 13, '13 files in "//OCR-D-I.*"')
    #     self.assertEqual(len(self.mets.find_all_files(ID="FILE_0001_IMAGE")), 1, '1 files with ID "FILE_0001_IMAGE"')
    #     self.assertEqual(len(self.mets.find_all_files(ID="//FILE_0005_.*")), 1, '1 files with ID "//FILE_0005_.*"')
    #     self.assertEqual(len(self.mets.find_all_files(mimetype='image/tiff')), 13, '13 image/tiff')
    #     self.assertEqual(len(self.mets.find_all_files(mimetype='//application/.*')), 22, '22 application/.*')
    #     self.assertEqual(len(self.mets.find_all_files(mimetype=MIMETYPE_PAGE)), 20, '20 ' + MIMETYPE_PAGE)
    #     self.assertEqual(len(self.mets.find_all_files(url='OCR-D-IMG/FILE_0005_IMAGE.tif')), 1, '1 xlink:href="OCR-D-IMG/FILE_0005_IMAGE.tif"')

# @mark.benchmark(group="build")
# def test_add_1(benchmark):
#     @benchmark
#     def result(): return  _build_mets(1, force=True)

mets_5 = None
mets_10 = None
mets_20 = None
mets_50 = None
mets_100 = None

mets2_5 = None
mets2_10 = None
mets2_20 = None
mets2_50 = None
mets2_100 = None

# ----- Build for 5-10-20-50-100 ----- #
@mark.benchmark(group="build", disable_gc=True)
def test_build_5_no_gc(benchmark):
    @benchmark
    def result():
        global mets_5
        mets_5 = _build_mets(5, force=True)

@mark.benchmark(group="build")
def test_build_5(benchmark):
    @benchmark
    def result():
        global mets_5
        mets_5 = _build_mets(5, force=True)

@mark.benchmark(group="build")
def test_build_10(benchmark):
    @benchmark
    def result():
        global mets_10
        mets_10 = _build_mets(10, force=True)

@mark.benchmark(group="build")
def test_build_20(benchmark):
    @benchmark
    def result():
        global mets_20
        mets_20 = _build_mets(20, force=True)

@mark.benchmark(group="build")
def test_build_50(benchmark):
    @benchmark
    def result():
        global mets_50
        mets_50 = _build_mets(50, force=True)

@mark.benchmark(group="build")
def test_build_100(benchmark):
    @benchmark
    def result():
        global mets_100
        mets_100 = _build_mets(100, force=True)

# ----- Search for 5-10-20-50-100 ----- #
@mark.benchmark(group="search")
def test_search_5(benchmark):
    @benchmark
    def ret(): 
        global mets_5
        benchmark_find_files(5, mets_5)

@mark.benchmark(group="search")
def test_search_10(benchmark):
    @benchmark
    def ret(): 
        global mets_10
        benchmark_find_files(10, mets_10)

@mark.benchmark(group="search")
def test_search_20(benchmark):
    @benchmark
    def ret(): 
        global mets_20
        benchmark_find_files(20, mets_20)

@mark.benchmark(group="search")
def test_search_50(benchmark):
    @benchmark
    def ret(): 
        global mets_50
        benchmark_find_files(50, mets_50)

@mark.benchmark(group="search")
def test_search_100(benchmark):
    @benchmark
    def ret():
        global mets_100
        benchmark_find_files(100, mets_100)

mets_5 = None
mets_10 = None
mets_20 = None
mets_50 = None
mets_100 = None


# ----- Build for 5-10-20-50-100 with optimized one ----- #
@mark.benchmark(group="build", disable_gc=True)
def test_build_5_no_gc_optimized(benchmark):
    @benchmark
    def result():
        global mets2_5
        mets2_5 = build_mets2(5, force=True)

@mark.benchmark(group="build")
def test_build_5_optimized(benchmark):
    @benchmark
    def result():
        global mets2_5 
        mets2_5 = build_mets2(5, force=True)

@mark.benchmark(group="build")
def test_build_10_opt(benchmark):
    @benchmark
    def result():
        global mets2_10
        mets2_10 = build_mets2(10, force=True)

@mark.benchmark(group="build")
def test_build_20_opt(benchmark):
    @benchmark
    def result():
        global mets2_20
        mets2_20 = build_mets2(20, force=True)

@mark.benchmark(group="build")
def test_build_50_opt(benchmark):
    @benchmark
    def result():
        global mets2_50
        mets2_50 = build_mets2(50, force=True)

@mark.benchmark(group="build")
def test_build_100_opt(benchmark):
    @benchmark
    def result():
        global mets2_100
        mets2_100 = build_mets2(100, force=True)

# ----- Search for 5-10-20-50-100 with optimized one ----- #

@mark.benchmark(group="search")
def test_search_5_opt(benchmark):
    @benchmark
    def ret():
        global mets2_5
        benchmark_find_files2(5, mets2_5)

@mark.benchmark(group="search")
def test_search_10_opt(benchmark):
    @benchmark
    def ret(): 
        global mets2_10
        benchmark_find_files2(10, mets2_10)

@mark.benchmark(group="search")
def test_search_20_opt(benchmark):
    @benchmark
    def ret(): 
        global mets2_20
        benchmark_find_files2(20, mets2_20)

@mark.benchmark(group="search")
def test_search_50_opt(benchmark):
    @benchmark
    def ret(): 
        global mets2_50
        benchmark_find_files2(50, mets2_50)

@mark.benchmark(group="search")
def test_search_100_opt(benchmark):
    @benchmark
    def ret(): 
        global mets2_100
        benchmark_find_files2(100, mets2_100)

mets2_5 = None
mets2_10 = None
mets2_20 = None
mets2_50 = None
mets2_100 = None

# @mark.benchmark(group="search", max_time=1)
# def test_search_10_pageid(benchmark):
#     @benchmark
#     def result(): return benchmark_find_files(10)

# @mark.benchmark(group="search", max_time=1)
# def test_search_20(benchmark):
#     @benchmark
#     def result(): return  benchmark_find_files(20)

# @mark.benchmark(group="search", max_time=1)
# def test_search_50(benchmark):
#     @benchmark
#     def result(): return  benchmark_find_files(50)


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

    #mets = _build_mets(2)
    #mets2 = build_mets2(2)

    #print(mets)
    #print("-------------------------------------------------------------")
    #print(mets2)

    #benchmark_find_files(2)
    #benchmark_find_files2(2)

    #print(mets2.mm_find_all_files(fileGrp='SEG-REG'))