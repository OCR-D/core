from click import option
#from ocrd_utils import parse_json_string_or_file

__all__ = ['parameter_option', 'parameter_override_option']


def _handle_param_option(ctx, param, value):
    return parse_json_string_or_file(*list(value))

parameter_option = option('-p', '--parameter',
                                help="Parameters, either JSON string or path to JSON file",
                                multiple=True,
                                default=['{}'],
                                # now handled in ocrd_cli_wrap_processor to resolve processor preset files
                                # callback=_handle_param_option
                                callback=lambda ctx, param, kv: list(kv))

parameter_override_option = option('-P', '--parameter-override',
                                help="Parameter override",
                                nargs=2,
                                multiple=True,
                                callback=lambda ctx, param, kv: kv)
                                # callback=lambda ctx, param, kv: {kv[0]: kv[1]})
