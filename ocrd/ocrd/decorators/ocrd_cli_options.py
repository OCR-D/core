from click import option, Path
from .parameter_option import parameter_option, parameter_override_option
from .loglevel_option import loglevel_option
from ocrd_network import QueueServerParamType, DatabaseParamType


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
        option('-m', '--mets', default="mets.xml"),
        option('-w', '--working-dir'),
        # TODO OCR-D/core#274
        # option('-I', '--input-file-grp', required=True),
        # option('-O', '--output-file-grp', required=True),
        option('-I', '--input-file-grp', default='INPUT'),
        option('-O', '--output-file-grp', default='OUTPUT'),
        option('-g', '--page-id'),
        option('--overwrite', is_flag=True, default=False),
        option('--profile', is_flag=True, default=False),
        option('--profile-file', type=Path(dir_okay=False, writable=True)),
        parameter_option,
        parameter_override_option,
        loglevel_option,
        option('--queue', type=QueueServerParamType()),
        option('--database', type=DatabaseParamType()),
        option('-C', '--show-resource'),
        option('-L', '--list-resources', is_flag=True, default=False),
        option('-J', '--dump-json', is_flag=True, default=False),
        option('-D', '--dump-module-dir', is_flag=True, default=False),
        option('-h', '--help', is_flag=True, default=False),
        option('-V', '--version', is_flag=True, default=False),
    ]
    for param in params:
        param(f)
    return f

