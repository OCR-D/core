import os

import click

from ocrd.resolver import Resolver
from ocrd.processor.base import run_processor

def ocrd_cli_wrap_processor(processorClass, mets=None, working_dir=None, cache_enabled=True, *args, **kwargs):
    if mets.find('://') == -1:
        mets = 'file://' + mets
    if mets.startswith('file://') and not os.path.exists(mets[len('file://'):]):
        raise Exception("File does not exist: %s" % mets)
    resolver = Resolver(cache_enabled=cache_enabled)
    workspace = resolver.workspace_from_url(mets, working_dir)
    run_processor(processorClass, mets, workspace=workspace, *args, **kwargs)

def ocrd_cli_options(f):
    """
    Implement MP CLI.

    Usage::

        import ocrd_click_cli from ocrd.utils

        @click.command()
        @ocrd_click_cli
        def cli(mets_url):
            print(mets_url)
    """
    params = [
        click.option('-m', '--mets', help="METS URL to validate", required=True),
        click.option('-w', '--working-dir', help="Working Directory"),
        click.option('-I', '--input-file-grp', help='File group(s) used as input.', default='INPUT'),
        click.option('-O', '--output-file-grp', help='File group(s) used as output.', default='OUTPUT'),
        click.option('-g', '--group-id', help="mets:file GROUPID"),
        click.option('-o', '--output-mets', help="METS URL to write resulting METS to"),
        click.option('-p', '--parameter', type=click.Path()),
        click.option('-l', '--log-level', help="Log level", type=click.Choice(['OFF', 'ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE']), default='INFO'),
    ]
    for param in params:
        param(f)
    return f
