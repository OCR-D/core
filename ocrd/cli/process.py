import json
import codecs

import click

from ocrd import run_cli, Resolver
from ocrd.decorators import ocrd_cli_options

# ----------------------------------------------------------------------
# ocrd process
# ----------------------------------------------------------------------

@click.command('process')
@ocrd_cli_options
@click.option('-T', '--ocrd-tool', multiple=True)
@click.argument('steps', nargs=-1)
def process_cli(mets_url, **kwargs):
    """
    Execute OCR-D processors for a METS file directly.
    """
    resolver = Resolver()
    workspace = resolver.workspace_from_url(mets_url)

    cmds = []
    for ocrd_tool_file in kwargs['ocrd_tool']:
        with codecs.open(ocrd_tool_file, encoding='utf-8') as f:
            obj = json.loads(f.read())
            for tool in obj['tools']:
                cmds.append(tool['binary'])

    for cmd in kwargs['steps']:
        if cmd not in cmds:
            raise Exception("Tool not registered: '%s'" % cmd)

    for cmd in kwargs['steps']:
        run_cli(cmd, mets_url, resolver, workspace)

    workspace.reload_mets()

    #  print('\n'.join(k + '=' + str(kwargs[k]) for k in kwargs))
    print(workspace)
