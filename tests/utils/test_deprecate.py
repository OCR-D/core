import click

from ocrd.cli import command_with_replaced_help

from tests.base import CapturingTestCase as TestCase, main

class TestDeprectateUtils(TestCase):

    def test_help_replace(self):
        @click.command('foo', help='foo foo foo', cls=command_with_replaced_help(('foo', 'bar')))
        def cli():
            pass
        _, out, _ = self.invoke_cli(cli, ['--help'])
        self.assertIn('bar bar bar', out)

if __name__ == "__main__":
    main(__file__)
