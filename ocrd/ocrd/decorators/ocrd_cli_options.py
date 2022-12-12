from click import option
from .parameter_option import parameter_option, parameter_override_option
from .loglevel_option import loglevel_option

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
        option('-m', '--mets', help="METS to process", default="mets.xml"),
        option('-w', '--working-dir', help="Working Directory"),
        # TODO OCR-D/core#274
        # option('-I', '--input-file-grp', help='File group(s) used as input. **required**'),
        # option('-O', '--output-file-grp', help='File group(s) used as output. **required**'),
        option('-I', '--input-file-grp', help='File group(s) used as input.', default='INPUT'),
        option('-O', '--output-file-grp', help='File group(s) used as output.', default='OUTPUT'),
        option('-g', '--page-id', help="ID(s) of the pages to process"),
        option('--overwrite', help="Overwrite the output file group or a page range (--page-id)", is_flag=True, default=False),
        option('-C', '--show-resource', help='Dump the content of processor resource RESNAME', metavar='RESNAME'),
        option('-L', '--list-resources', is_flag=True, default=False, help='List names of processor resources'),
        parameter_option,
        parameter_override_option,
        option('-J', '--dump-json', help="Dump tool description as JSON and exit", is_flag=True, default=False),
        option('-D', '--dump-module-dir', help="Print processor's 'moduledir' of resourcess", is_flag=True, default=False),
        loglevel_option,
        option('-V', '--version', help="Show version", is_flag=True, default=False),
        option('-h', '--help', help="This help message", is_flag=True, default=False),
        option('--profile', help="Enable profiling", is_flag=True, default=False),
        option('--profile-file', help="Write cProfile stats to this file. Implies --profile"),
    ]
    for param in params:
        param(f)
    return f
