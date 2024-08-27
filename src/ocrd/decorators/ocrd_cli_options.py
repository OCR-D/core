import click
from click import option, Path, group, command, argument
from ocrd_utils import DEFAULT_METS_BASENAME
from ocrd_network import AgentType
from .parameter_option import parameter_option, parameter_override_option
from .loglevel_option import loglevel_option
from ocrd_network import (
    DatabaseParamType,
    ServerAddressParamType,
    QueueServerParamType
)


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
    # XXX Note that the `--help` output is statically generate_processor_help
    params = [
        option('-m', '--mets', help="METS to process", default=DEFAULT_METS_BASENAME),
        option('-w', '--working-dir', help="Working Directory"),
        option('-U', '--mets-server-url', help="METS server URL. Starts with http:// then TCP, otherwise unix socket path"),
        option('-I', '--input-file-grp', default=None),
        option('-O', '--output-file-grp', default=None),
        option('-g', '--page-id'),
        option('--overwrite', is_flag=True, default=False),
        option('--profile', is_flag=True, default=False),
        option('--profile-file', type=Path(dir_okay=False, writable=True)),
        parameter_option,
        parameter_override_option,
        loglevel_option,
        option('--address', type=ServerAddressParamType()),
        option('--queue', type=QueueServerParamType()),
        option('--database', type=DatabaseParamType()),
        option('-C', '--show-resource'),
        option('-L', '--list-resources', is_flag=True, default=False),
        option('-J', '--dump-json', is_flag=True, default=False),
        option('-D', '--dump-module-dir', is_flag=True, default=False),
        option('-h', '--help', is_flag=True, default=False),
        option('-V', '--version', is_flag=True, default=False),
        option('--log-filename', default=None),
        # Subcommand, only used for 'worker'/'server'. Cannot be handled in
        # click because processors use the @command decorator and even if they
        # were using `group`, you cannot combine have a command with
        # subcommands. So we have to work around that by creating a
        # pseudo-subcommand handled in ocrd_cli_wrap_processor
        argument('subcommand', nargs=1, required=False,
                 type=click.Choice([AgentType.PROCESSING_WORKER, AgentType.PROCESSOR_SERVER])),
    ]
    for param in params:
        param(f)
    return f
