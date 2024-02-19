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
    rabbitmq_publisher.publish_to_queue(
        queue_name=DEFAULT_QUEUE,
        message="RabbitMQ test 123",
        exchange_name=DEFAULT_EXCHANGER_NAME,
        properties=test_properties
    )
    rabbitmq_publisher.publish_to_queue(
        queue_name=DEFAULT_QUEUE,
        message="RabbitMQ test 456",
        exchange_name=DEFAULT_EXCHANGER_NAME,
        properties=test_properties
    )
    assert rabbitmq_publisher.message_counter == 2

    # Consume the 1st message
    method_frame, header_frame, message = rabbitmq_consumer.get_one_message(
        queue_name=DEFAULT_QUEUE,
        auto_ack=True
    )
    assert method_frame.delivery_tag == 1  # 1st delivered message to this queue
    assert method_frame.message_count == 1  # messages left in the queue
    assert method_frame.redelivered is False
    assert method_frame.exchange == DEFAULT_EXCHANGER_NAME
    assert method_frame.routing_key == DEFAULT_QUEUE
    # It's possible to assert header_frame the same way
    assert message.decode() == "RabbitMQ test 123"

    # Consume the 2nd message
    method_frame, header_frame, message = rabbitmq_consumer.get_one_message(
        queue_name=DEFAULT_QUEUE,
        auto_ack=True
    )
    assert method_frame.delivery_tag == 2  # 2nd delivered message to this queue
    assert method_frame.message_count == 0  # messages left in the queue
    assert method_frame.redelivered is False
    assert method_frame.exchange == DEFAULT_EXCHANGER_NAME
    assert method_frame.routing_key == DEFAULT_QUEUE
    # It's possible to assert header_frame the same way
    assert message.decode() == "RabbitMQ test 456"


def test_rmq_publish_then_consume_ocrd_message(rabbitmq_publisher, rabbitmq_consumer):
    ocrd_processing_message = {
        "job_id": "Test_job_id",
        "workflow_id": "Test_workflow_id",
        "workspace_id": "Test_workspace_id"
    }
    message_bytes = dumps(ocrd_processing_message)
    rabbitmq_publisher.publish_to_queue(
        queue_name=DEFAULT_QUEUE,
        message=message_bytes,
        exchange_name=DEFAULT_EXCHANGER_NAME,
        properties=None
    )

    method_frame, header_frame, message = rabbitmq_consumer.get_one_message(
        queue_name=DEFAULT_QUEUE,
        auto_ack=True
    )
    assert method_frame.message_count == 0  # messages left in the queue
    decoded_message = loads(message)
    assert decoded_message["job_id"] == "Test_job_id"
    assert decoded_message["workflow_id"] == "Test_workflow_id"
    assert decoded_message["workspace_id"] == "Test_workspace_id"
