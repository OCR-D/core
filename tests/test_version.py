from ocrd_utils import VERSION
from tests.base import TestCase, main


class TestVersion(TestCase):

    def runTest(self):
        self.assertIsNot(VERSION, None)

if __name__ == '__main__':
    main()
