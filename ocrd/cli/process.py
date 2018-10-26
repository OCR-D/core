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
def process_cli(mets, steps, **kwargs):
    """
    Execute OCR-D processor executables for a METS file.

    Run each of the STEPS executables one after another.

    Order of comma-separated values for -I, -O, -p corresponds to order of steps.
    """
    resolver = Resolver()
    workspace = resolver.workspace_from_url(mets)

    cmds = []
    for ocrd_tool_file in kwargs['ocrd_tool']:
        with codecs.open(ocrd_tool_file, encoding='utf-8') as f:
            obj = json.loads(f.read())
            for tool in obj['tools'].values():
                cmds.append(tool['executable'])

    for cmd in steps:
        if cmd not in cmds:
            raise Exception("Tool not registered: '%s'" % cmd)

    # fixme: this really should be coming from workflow engine (giving steps, i/o fileGrps, parameter files)
    # fixme: using the command line here is inefficient
    # fixme: someone should go and check if the first input_file_grp actually exists
    if 'input_file_grp' not in kwargs:
        raise Exception("Need input_file_grp USE(s)")
    if 'output_file_grp' not in kwargs:
        raise Exception("Need output_file_grp USE(s)")
    if 'parameter' not in kwargs:
        raise Exception("Need parameter file(s)")
    input_file_grps = kwargs['input_file_grp'].split(',')
    if len(input_file_grps) != len(steps):
        raise Exception("Number of input_file_grp arguments (%d) does not match number of steps (%d)" % (len(input_file_grps), len(steps)))
    output_file_grps = kwargs['output_file_grp'].split(',')
    if len(output_file_grps) != len(steps):
        raise Exception("Number of output_file_grp arguments (%d) does not match number of steps (%d)" % (len(output_file_grps), len(steps)))
    parameters = kwargs['parameter'].split(',')
    if len(parameters) != len(steps):
        raise Exception("Number of parameter files (%d) does not match number of steps (%d)" % (len(parameters), len(steps)))

    for cmd, input_file_grp, output_file_grp, parameter in zip(steps, input_file_grps, output_file_grps, parameters):
        run_cli(cmd, mets, resolver, workspace,
                log_level=kwargs['log_level'],
                group_id=kwargs['group_id'],
                input_file_grp=input_file_grp,
                output_file_grp=output_file_grp,
                parameter=parameter)

    workspace.reload_mets()

    #  print('\n'.join(k + '=' + str(kwargs[k]) for k in kwargs))
    print(workspace)
