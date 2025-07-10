from contextlib import nullcontext
from json import dumps
from pathlib import Path
from typing import List, Optional
from tempfile import NamedTemporaryFile
from logging.config import fileConfig

from ocrd.processor.helpers import run_cli, run_processor
from ocrd_utils import redirect_stderr_and_stdout_to_file, initLogging
from .utils import get_ocrd_workspace_instance


# A wrapper for run_processor() and run_cli()
def invoke_processor(
    processor_class,
    executable: str,
    abs_path_to_mets: str,
    input_file_grps: List[str],
    output_file_grps: List[str],
    page_id: str,
    parameters: dict,
    mets_server_url: Optional[str] = None,
    log_filename: Optional[Path] = None,
    log_level: str = "DEBUG"
) -> None:
    if not (processor_class or executable):
        raise ValueError("Missing processor class and executable")
    input_file_grps_str = ','.join(input_file_grps)
    output_file_grps_str = ','.join(output_file_grps)

    workspace = get_ocrd_workspace_instance(mets_path=abs_path_to_mets, mets_server_url=mets_server_url)
    if processor_class:
        with NamedTemporaryFile(mode='w') as cfgfile:
            cfgfile.write("""
[loggers]
keys=root,ocrd,ocrd_network,tensorflow,shapely_geos
[handlers]
keys=fileHandler
[formatters]
keys=defaultFormatter
[logger_root]
level=WARNING
handlers=fileHandler
[logger_ocrd]
level=INFO
handlers=
qualname=ocrd
[logger_ocrd_network]
level=INFO
handlers=
qualname=ocrd_network
[logger_tensorflow]
level=ERROR
handlers=
qualname=tensorflow
[logger_shapely_geos]
level=ERROR
handlers=
qualname=shapely.geos
[handler_fileHandler]
class=FileHandler
formatter=defaultFormatter
args=('{log_filename}','a+')
[formatter_defaultFormatter]
format=%(asctime)s.%(msecs)03d %(levelname)s %(name)s - %(message)s
datefmt=%H:%M:%S
""".format(log_filename=log_filename))
            cfgfile.flush()
            # deletes all existing handlers
            fileConfig(cfgfile.name)
        try:
            run_processor(
                processorClass=processor_class,
                workspace=workspace,
                input_file_grp=input_file_grps_str,
                output_file_grp=output_file_grps_str,
                page_id=page_id,
                parameter=parameters,
                instance_caching=True,
                mets_server_url=mets_server_url,
                log_level=log_level
            )
        except Exception as error:
            raise RuntimeError(f"Python executable '{processor_class.__dict__}', error: {error}")
    else:
        return_code = run_cli(
            executable=executable,
            workspace=workspace,
            mets_url=abs_path_to_mets,
            input_file_grp=input_file_grps_str,
            output_file_grp=output_file_grps_str,
            page_id=page_id,
            parameter=dumps(parameters),
            mets_server_url=mets_server_url,
            log_level=log_level,
            log_filename=log_filename
        )
        if return_code != 0:
            raise RuntimeError(f"CLI executable '{executable}' exited with code: {return_code}")
