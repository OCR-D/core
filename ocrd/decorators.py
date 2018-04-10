import os

import click

from ocrd.resolver import Resolver
from ocrd.processor.base import run_processor

def ocrd_cli_wrap_processor(processorClass, mets_url=None, working_dir=None, cache_enabled=True, *args, **kwargs):
    if mets_url.find('://') == -1:
        mets_url = 'file://' + mets_url
    if mets_url.startswith('file://') and not os.path.exists(mets_url[len('file://'):]):
        raise Exception("File does not exist: %s" % mets_url)
    resolver = Resolver(cache_enabled=cache_enabled)
    workspace = resolver.workspace_from_url(mets_url, working_dir)
    run_processor(processorClass, mets_url, workspace=workspace, *args, **kwargs)

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
        click.option('-m', '--mets-url', help="METS URL to validate", required=True),
        click.option('-o', '--output-mets', help="METS URL to write resulting METS to"),
        click.option('-p', '--parameter', type=click.Path()),
        click.option('-w', '--working-dir', help="Working Directory"),
        click.option('-g', '--group-id', help="mets:file GROUPID"),
        click.option('-I', '--input-filegrp', help='File group(s) used as input.', default='INPUT'),
        click.option('-O', '--output-filegrp', help='File group(s) used as output.', default='OUTPUT'),
    ]
    for param in params:
        param(f)
    return f
