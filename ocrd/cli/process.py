import os
from shlex import split as shlex_split
from distutils.spawn import find_executable as which # pylint: disable=import-error,no-name-in-module

import click

from ..processor.base import run_cli
from ..logging import getLogger
from ..resolver import Resolver
from ..decorators import ocrd_loglevel

class ProcessorTask(object):

    @classmethod
    def parse(cls, argstr):
        tokens = shlex_split(argstr)
        executable = 'ocrd-%s' % tokens.pop(0)
        input_file_grps = []
        output_file_grps = []
        parameter_path = None
        while tokens:
            if tokens[0] == '-I':
                for grp in tokens[1].split(','):
                    input_file_grps.append(grp)
                tokens = tokens[2:]
            elif tokens[0] == '-O':
                for grp in tokens[1].split(','):
                    output_file_grps.append(grp)
                tokens = tokens[2:]
            elif tokens[0] == '-p':
                parameter_path = tokens[1]
                tokens = tokens[2:]
            else:
                raise Exception("Failed parsing task description '%s' with tokens remaining: '%s'" % (argstr, tokens))

        if not which(executable):
            raise Exception("Executable not found in PATH: %s" % executable)
        if parameter_path and not os.access(parameter_path, os.R_OK):
            raise Exception("Parameter file not readable: %s" % parameter_path)
        if not input_file_grps:
            raise Exception("Task must have input file group")
        if not output_file_grps:
            raise Exception("Task must have output file group")
        return ProcessorTask(executable, input_file_grps, output_file_grps, parameter_path)

    def __init__(self, executable, input_file_grps, output_file_grps, parameter_path=None):
        self.executable = executable
        self.input_file_grps = input_file_grps
        self.output_file_grps = output_file_grps
        self.parameter_path = parameter_path

    def __str__(self):
        ret = '%s -I %s -O %s' % (
            self.executable.replace('ocrd-', '', 1),
            ','.join(self.input_file_grps),
            ','.join(self.output_file_grps))
        if self.parameter_path:
            ret += ' -p %s' % self.parameter_path
        return ret

# ----------------------------------------------------------------------
# ocrd process
# ----------------------------------------------------------------------
@click.command('process')
@ocrd_loglevel
@click.option('-m', '--mets', help="METS to process")
@click.option('-g', '--group-id', help="ID(s) of the pages to process")
@click.argument('tasks', nargs=-1, required=True)
def process_cli(log_level, mets, group_id, tasks):
    """
    Process a series of tasks
    """
    log = getLogger('ocrd.cli.process')

    resolver = Resolver()
    task_strs = tasks
    mets_url = mets
    workspace = resolver.workspace_from_url(mets_url)
    tasks = [ProcessorTask.parse(task_str) for task_str in task_strs]

    for task in tasks:

        # check input file groups are in mets
        for input_file_grp in task.input_file_grps:
            if not input_file_grp in workspace.mets.file_groups:
                raise Exception("Unmet requirement: expected input file group not contained in mets: %s" % input_file_grp)

        for output_file_grp in task.output_file_grps:
            if output_file_grp in workspace.mets.file_groups:
                raise Exception("Conflict: output file group already contained in mets: %s" % output_file_grp)

        log.info("Start processing task '%s'", task)

        # execute cli
        returncode = run_cli(
            task.executable,
            mets_url,
            resolver,
            workspace,
            log_level=log_level,
            group_id=group_id,
            input_file_grp=','.join(task.input_file_grps),
            output_file_grp=','.join(task.output_file_grps),
            parameter=task.parameter_path
        )

        # check return code
        if returncode != 0:
            raise Exception("%s exited with non-zero return value %s" % (task.executable, returncode))

        log.info("Finished processing task '%s'", task)

        # reload mets
        workspace.reload_mets()

        # check output file groups are in mets
        for output_file_grp in task.output_file_grps:
            if not output_file_grp in workspace.mets.file_groups:
                raise Exception("Invalid state: expected output file group not in mets: %s" % output_file_grp)

    log.info("Finished")
