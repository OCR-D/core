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
@click.option('-T', '--ocrd-tool', multiple=True, type=click.Path(exists=True, dir_okay=False), help='register all executables from a ocrd-tool.json file')
@click.argument('steps', nargs=-1)
def process_cli(mets, **kwargs):
    """
    Execute OCR-D processors for a METS file directly.
    
    Run each of the STEPS executables one after another.
    """
    resolver = Resolver()
    workspace = resolver.workspace_from_url(mets)

    cmds = []
    for ocrd_tool_file in kwargs['ocrd_tool']:
        with codecs.open(ocrd_tool_file, encoding='utf-8') as f:
            obj = json.loads(f.read())
            for tool in obj['tools'].values():
                cmds.append(tool['executable'])

    for cmd in kwargs['steps']:
        if cmd not in cmds:
            raise Exception("Tool not registered: '%s'" % cmd)

    for cmd in kwargs['steps']:
        run_cli(cmd, mets, resolver, workspace)

    workspace.reload_mets()

    #  print('\n'.join(k + '=' + str(kwargs[k]) for k in kwargs))
    print(workspace)
