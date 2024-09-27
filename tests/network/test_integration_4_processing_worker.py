from pathlib import Path
from pika import BasicProperties
from src.ocrd.processor.builtin.dummy_processor import DummyProcessor
from src.ocrd_network.constants import JobState
from src.ocrd_network.database import sync_db_create_workspace, sync_db_create_processing_job
from src.ocrd_network.logging_utils import get_processing_job_logging_file_path
from src.ocrd_network.models import DBProcessorJob
from src.ocrd_network.processing_worker import ProcessingWorker
from src.ocrd_network.rabbitmq_utils import OcrdProcessingMessage, OcrdResultMessage
from src.ocrd_network.utils import generate_created_time, generate_id
from tests.base import assets
from tests.network.config import test_config


def test_processing_worker_process_message():
    workspace_root = "kant_aufklaerung_1784/data"
    path_to_mets = assets.path_to(f"{workspace_root}/mets.xml")
    assert Path(path_to_mets).exists()
    test_job_id = generate_id()
    test_created_time = generate_created_time()
    input_file_grp = "OCR-D-IMG"
    output_file_grp = f"OCR-D-DUMMY-TEST-WORKER-{test_job_id}"
    page_id = "PHYS_0017,PHYS_0020"
    # Notice, the name is intentionally set differently from "ocrd-dummy" to prevent
    # wrong reads from the deployed dummy worker (part of the processing server integration test)
    processor_name = "ocrd-dummy-test"
    result_queue_name = f"{processor_name}-result"
    ocrd_tool = DummyProcessor(None).metadata

    processing_worker = ProcessingWorker(
        rabbitmq_addr=test_config.RABBITMQ_URL,
        mongodb_addr=test_config.DB_URL,
        processor_name=processor_name,
        ocrd_tool=ocrd_tool,
        processor_class=DummyProcessor
    )
    processing_worker.connect_publisher(enable_acks=True)
    assert processing_worker.rmq_publisher
    processing_worker.connect_consumer()
    assert processing_worker.rmq_consumer

    # Create the workspace DB entry if not already existing
    sync_db_create_workspace(mets_path=path_to_mets)
    # Create the processing job DB entry
    sync_db_create_processing_job(
        db_processing_job=DBProcessorJob(
            job_id=test_job_id,
            processor_name=processor_name,
            created_time=test_created_time,
            path_to_mets=path_to_mets,
            workspace_id=None,
            input_file_grps=[input_file_grp],
            output_file_grps=[output_file_grp],
            page_id=page_id,
            parameters={},
            result_queue_name=result_queue_name,
            callback_url=None,
            internal_callback_url=None
        )
    )

    # PUSH/Publish the ocrd processing message
    ocrd_processing_message = OcrdProcessingMessage(
        job_id=test_job_id,
        processor_name=processor_name,
        created_time=test_created_time,
        path_to_mets=path_to_mets,
        workspace_id=None,
        input_file_grps=[input_file_grp],
        output_file_grps=[output_file_grp],
        page_id=page_id,
        parameters={},
        result_queue_name=result_queue_name,
        callback_url=None,
        internal_callback_url=None
    )
    encoded_message = OcrdProcessingMessage.encode_yml(ocrd_processing_message)
    test_properties = BasicProperties(
        app_id="ocrd_network_testing",
        content_type="application/json",
        headers={"Test Header": "Test Value"}
    )
    # Push the ocrd processing message to the RabbitMQ
    processing_worker.rmq_publisher.publish_to_queue(
        queue_name=processor_name, message=encoded_message, properties=test_properties
    )
    # The queue should have a single message inside
    assert processing_worker.rmq_publisher.message_counter == 1

    # PULL/Consume the ocrd processing message
    method_frame, header_frame, processing_message = processing_worker.rmq_consumer.get_one_message(
        queue_name=processor_name, auto_ack=True
    )
    assert method_frame.message_count == 0  # Messages left in the queue
    assert method_frame.redelivered is False
    assert method_frame.routing_key == processor_name

    decoded_processing_message = OcrdProcessingMessage.decode_yml(ocrd_processing_message=processing_message)

    # Process the ocrd processing message
    processing_worker.process_message(processing_message=decoded_processing_message)

    # Check the existence of the results locally
    assert Path(assets.path_to(f"{workspace_root}/{output_file_grp}")).exists()
    path_to_log_file = get_processing_job_logging_file_path(job_id=test_job_id)
    assert Path(path_to_log_file).exists()

    # PULL/Consume the ocrd result message for verification (pushed by the process_message method)
    method_frame, header_frame, result_message = processing_worker.rmq_consumer.get_one_message(
        queue_name=result_queue_name, auto_ack=True
    )
    assert method_frame.message_count == 0  # Messages left in the queue
    assert method_frame.redelivered is False
    assert method_frame.routing_key == result_queue_name

    decoded_result_message = OcrdResultMessage.decode_yml(result_message)
    assert decoded_result_message.job_id == test_job_id
    assert decoded_result_message.state == JobState.success
    assert decoded_result_message.path_to_mets == path_to_mets
