from pika import BasicProperties
from pickle import dumps, loads
from tests.network.config import test_config

DEFAULT_EXCHANGER_NAME = test_config.DEFAULT_EXCHANGER_NAME
DEFAULT_QUEUE = test_config.DEFAULT_QUEUE


def test_rmq_publish_then_consume_2_messages(rabbitmq_publisher, rabbitmq_consumer):
    test_headers = {"Test Header": "Test Value"}
    test_properties = BasicProperties(
        app_id="webapi-processing-broker",
        content_type="application/json",
        headers=test_headers
    )
    message1 = "RabbitMQ test 123"
    message2 = "RabbitMQ test 456"
    rabbitmq_publisher.publish_to_queue(
        queue_name=DEFAULT_QUEUE, message=message1, exchange_name=DEFAULT_EXCHANGER_NAME, properties=test_properties
    )
    rabbitmq_publisher.publish_to_queue(
        queue_name=DEFAULT_QUEUE, message=message2, exchange_name=DEFAULT_EXCHANGER_NAME, properties=test_properties
    )
    assert rabbitmq_publisher.message_counter == 2

    # Consume the 1st message
    method_frame, header_frame, message = rabbitmq_consumer.get_one_message(queue_name=DEFAULT_QUEUE, auto_ack=True)
    assert method_frame.message_count == 1  # messages left in the queue
    assert method_frame.redelivered is False
    assert method_frame.exchange == DEFAULT_EXCHANGER_NAME
    assert method_frame.routing_key == DEFAULT_QUEUE
    # It's possible to assert header_frame the same way
    assert message.decode() == message1

    # Consume the 2nd message
    method_frame, header_frame, message = rabbitmq_consumer.get_one_message(queue_name=DEFAULT_QUEUE, auto_ack=True)
    assert method_frame.message_count == 0  # messages left in the queue
    assert method_frame.redelivered is False
    assert method_frame.exchange == DEFAULT_EXCHANGER_NAME
    assert method_frame.routing_key == DEFAULT_QUEUE
    # It's possible to assert header_frame the same way
    assert message.decode() == message2


def test_rmq_publish_then_consume_ocrd_message(rabbitmq_publisher, rabbitmq_consumer):
    test_job_id = "test_job_id"
    test_wf_id = "test_workflow_id"
    test_ws_id = "test_ws_id"
    ocrd_processing_message = {"job_id": test_job_id, "workflow_id": test_wf_id, "workspace_id": test_ws_id}
    message_bytes = dumps(ocrd_processing_message)
    rabbitmq_publisher.publish_to_queue(
        queue_name=DEFAULT_QUEUE, message=message_bytes, exchange_name=DEFAULT_EXCHANGER_NAME, properties=None
    )

    method_frame, header_frame, message = rabbitmq_consumer.get_one_message(queue_name=DEFAULT_QUEUE, auto_ack=True)
    assert method_frame.message_count == 0  # messages left in the queue
    assert method_frame.redelivered is False
    assert method_frame.exchange == DEFAULT_EXCHANGER_NAME
    assert method_frame.routing_key == DEFAULT_QUEUE
    decoded_message = loads(message)
    assert decoded_message["job_id"] == test_job_id
    assert decoded_message["workflow_id"] == test_wf_id
    assert decoded_message["workspace_id"] == test_ws_id
