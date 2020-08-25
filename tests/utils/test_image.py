from tests.base import TestCase, main, assets
from ocrd import Resolver
from ocrd_modelfactory import page_from_file
from ocrd_utils import (
    polygon_for_parent,
    pushd_popd,

    MIMETYPE_PAGE
)
class TestImageUtils(TestCase):

    def test_polygon_for_parent(self):
        resolver = Resolver()
        with pushd_popd(assets.path_to('gutachten/data')):
            ws = resolver.workspace_from_url(assets.path_to('gutachten/data/mets.xml'))
            input_file = ws.download_file(ws.mets.find_files(mimetype=MIMETYPE_PAGE)[0])
            pcgts = page_from_file(input_file)
            page = pcgts.get_Page()
            page_image, page_coords, page_image_info = ws.image_from_page(page, 'f')
            width = page_image_info.width
            height = page_image_info.height
            p = polygon_for_parent([(-10, -10), (width + 10, -10), (width + 10, height + 10), (-10, height + 10)], page)
            self.assertEqual(p, [(0, 0), (0, height), (width, height), (width, 0)])


if __name__ == '__main__':
    main(__file__)
