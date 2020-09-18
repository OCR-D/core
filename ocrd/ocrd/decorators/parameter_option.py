from click import option
from ocrd_utils import parse_json_string_or_file

__all__ = ['parameter_option', 'parameter_override_option']


def _handle_param_option(ctx, param, value):
    return parse_json_string_or_file(*list(value))

parameter_option = option('-p', '--parameter',
                                help="Parameters, either JSON string or path to JSON file",
                                multiple=True,
                                default=['{}'],
                                callback=_handle_param_option)

parameter_override_option = option('-P', '--parameter-override',
                                help="Parameter override",
                                nargs=2,
                                multiple=True,
                                callback=lambda ctx, param, kv: kv)
                                # callback=lambda ctx, param, kv: {kv[0]: kv[1]})
