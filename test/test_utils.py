from test.base import TestCase, main
from ocrd.utils import (
    points_from_xywh,
    xywh_from_points,
    polygon_from_points
)

class TestResolver(TestCase):

    #  def runTest(self):

    def test_points_from_xywh(self):
        self.assertEqual(
            points_from_xywh({'x': 100, 'y': 100, 'w': 100, 'h': 100}),
            '100,100 200,100 200,200 100,200'
        )

    def test_xywh_from_points(self):
        self.assertEqual(
            xywh_from_points('100,100 200,100 200,200 100,200'),
            {'x': 100, 'y': 100, 'w': 100, 'h': 100})

    def test_polygon_from_points(self):
        self.assertEqual(
            polygon_from_points('100,100 200,100 200,200 100,200'),
            [[100, 100], [200, 100], [200, 200], [100, 200]])

if __name__ == '__main__':
    main()
