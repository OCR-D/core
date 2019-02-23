from tests.base import TestCase, main
from ocrd_utils import VERSION

class TestVersion(TestCase):

    def runTest(self):
        self.assertIsNot(VERSION, None)

if __name__ == '__main__':
    main()
