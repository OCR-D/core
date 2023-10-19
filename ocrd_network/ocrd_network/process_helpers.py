import json
from typing import List, Optional
from contextlib import nullcontext

from ocrd.processor.helpers import run_cli, run_processor
from .utils import get_ocrd_workspace_instance
from ocrd_utils import redirect_stderr_and_stdout_to_file, initLogging


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
        log_filename: str = None,
) -> None:
    if not (processor_class or executable):
        raise ValueError('Missing processor class and executable')
    input_file_grps_str = ','.join(input_file_grps)
    output_file_grps_str = ','.join(output_file_grps)

    workspace = get_ocrd_workspace_instance(
        mets_path=abs_path_to_mets,
        mets_server_url=mets_server_url
    )

    if processor_class:
        ctx_mgr = redirect_stderr_and_stdout_to_file(log_filename) if log_filename else nullcontext()
        with ctx_mgr:
            initLogging(force_reinit=True)
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
                    log_level='DEBUG'
                )
            except Exception as e:
                raise RuntimeError(f"Python executable '{processor_class.__dict__}' exited with: {e}")
    else:
        return_code = run_cli(
            executable=executable,
            workspace=workspace,
            mets_url=abs_path_to_mets,
            input_file_grp=input_file_grps_str,
            output_file_grp=output_file_grps_str,
            page_id=page_id,
            parameter=json.dumps(parameters),
            mets_server_url=mets_server_url,
            log_level='DEBUG',
            log_filename=log_filename
        )
        if return_code != 0:
            raise RuntimeError(f"CLI executable '{executable}' exited with: {return_code}")
