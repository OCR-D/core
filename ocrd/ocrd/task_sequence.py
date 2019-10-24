import json
from shlex import split as shlex_split
from distutils.spawn import find_executable as which # pylint: disable=import-error,no-name-in-module
from subprocess import run, PIPE

from ocrd_utils import getLogger, parse_json_string_or_file
from ocrd.processor.base import run_cli
from ocrd.resolver import Resolver

class ProcessorTask():

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
        return ProcessorTask(executable, input_file_grps, output_file_grps, parameter_path)

    def __init__(self, executable, input_file_grps, output_file_grps, parameter_path=None):
        self.executable = executable
        self.input_file_grps = input_file_grps
        self.output_file_grps = output_file_grps
        self.parameter_path = parameter_path

    def validate(self):
        if not which(self.executable):
            raise Exception("Executable not found in PATH: %s" % self.executable)
        result = run([self.executable, '--dump-json'], stdout=PIPE, check=True, universal_newlines=True)
        ocrd_tool_json = json.loads(result.stdout)
        # TODO check for required parameters in ocrd_tool
        if self.parameter_path:
            parse_json_string_or_file(self.parameter_path)
        if not self.input_file_grps:
            raise Exception("Task must have input file group")
        if 'output_file_grp' in ocrd_tool_json and not self.output_file_grps:
            raise Exception("Processor requires output_file_grp but none was provided.")
        return True

    def __str__(self):
        ret = '%s -I %s -O %s' % (
            self.executable.replace('ocrd-', '', 1),
            ','.join(self.input_file_grps),
            ','.join(self.output_file_grps))
        if self.parameter_path:
            ret += ' -p %s' % self.parameter_path
        return ret

def run_tasks(mets, log_level, page_id, task_strs):
    resolver = Resolver()
    workspace = resolver.workspace_from_url(mets)
    log = getLogger('ocrd.task_sequence')
    tasks = [ProcessorTask.parse(task_str) for task_str in task_strs]

    for task in tasks:

        task.validate()

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
            mets,
            resolver,
            workspace,
            log_level=log_level,
            page_id=page_id,
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


