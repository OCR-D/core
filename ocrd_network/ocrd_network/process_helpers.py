import json
from typing import List

from ocrd import Resolver
from ocrd.processor.helpers import run_cli, run_processor


# A wrapper for run_processor() and run_cli()
def run_single_execution(
        ProcessorClass,
        executable: str,
        abs_path_to_mets: str,
        input_file_grps: List[str],
        output_file_grps: List[str],
        page_id: str,
        parameters: dict,
) -> None:
    if not (ProcessorClass or executable):
        raise ValueError(f'Missing processor class and executable')
    input_file_grps_str = ','.join(input_file_grps)
    output_file_grps_str = ','.join(output_file_grps)
    workspace = Resolver().workspace_from_url(abs_path_to_mets)
    if ProcessorClass:
        try:
            run_processor(
                processorClass=ProcessorClass,
                workspace=workspace,
                input_file_grp=input_file_grps_str,
                output_file_grp=output_file_grps_str,
                page_id=page_id,
                parameter=parameters,
                instance_caching=True
            )
        except Exception as e:
            raise RuntimeError(f"Python executable '{executable}' exited with: {e}")
    else:
        return_code = run_cli(
            executable=executable,
            workspace=workspace,
            mets_url=abs_path_to_mets,
            input_file_grp=input_file_grps_str,
            output_file_grp=output_file_grps_str,
            page_id=page_id,
            parameter=json.dumps(parameters)
        )
        if return_code != 0:
            raise RuntimeError(f"CLI executable '{executable}' exited with: {return_code}")
