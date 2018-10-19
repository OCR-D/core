from test.base import TestCase, assets, main # pylint: disable=unused-import

from ocrd.model import OcrdAgent

# pylint: disable=no-member
class TestOcrdAgent(TestCase):

    def test_basic1(self):
        ag = OcrdAgent(role='FOO')
        self.assertEqual(ag.role, 'FOO')

    def test_basic2(self):
        ag = OcrdAgent(otherrole='BAR')
        self.assertEqual(ag.role, 'OTHER')
        self.assertEqual(ag.otherrole, 'BAR')

    def test_basic3(self):
        ag = OcrdAgent(name='foobar')
        self.assertEqual(ag.name, 'foobar')
        ag.name = 'barfoo'
        self.assertEqual(ag.name, 'barfoo')

    def test_basic4(self):
        ag = OcrdAgent(othertype='foobar')
        self.assertEqual(ag.type, 'OTHER')
        #  print(ag)

if __name__ == '__main__':
    main()
