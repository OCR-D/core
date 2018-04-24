from test.base import TestCase, main
import ocrd

class TestVersion(TestCase):

    def runTest(self):
        self.assertIsNot(ocrd.VERSION, None)

if __name__ == '__main__':
    main()
