from __future__ import annotations
from logging import Logger
from typing import Any, Dict, List, Optional, Union

from ..constants import DOCKER_IMAGE_MONGO_DB, DOCKER_IMAGE_RABBIT_MQ, DOCKER_RABBIT_MQ_FEATURES
from ..database import verify_mongodb_available
from ..rabbitmq_utils import verify_rabbitmq_available
from .connection_clients import create_docker_client


class DataNetworkService:
    def __init__(
        self, host: str, port: int, ssh_username: str, ssh_keypath: str, ssh_password: str,
        cred_username: str, cred_password: str, service_url: str, skip_deployment: bool, pid: Optional[Any]
    ) -> None:
        self.host = host
        self.port = port
        self.ssh_username = ssh_username
        self.ssh_keypath = ssh_keypath
        self.ssh_password = ssh_password
        self.cred_username = cred_username
        self.cred_password = cred_password
        self.service_url = service_url
        self.skip_deployment = skip_deployment
        self.pid = pid

    @staticmethod
    def deploy_docker_service(
        logger: Logger, service_data: Union[DataMongoDB, DataRabbitMQ], image: str, env: Optional[List[str]],
        ports_mapping: Optional[Dict], detach: bool = True, remove: bool = True
    ) -> None:
        if not service_data or not service_data.host:
            message = f"Deploying '{image}' has failed - missing service configurations."
            logger.exception(message)
            raise RuntimeError(message)
        logger.info(f"Deploying '{image}' service on '{service_data.host}', detach={detach}, remove={remove}")
        logger.info(f"Ports mapping: {ports_mapping}")
        logger.info(f"Environment: {env}")
        client = create_docker_client(
            service_data.host, service_data.ssh_username, service_data.ssh_password, service_data.ssh_keypath
        )
        result = client.containers.run(image=image, detach=detach, remove=remove, ports=ports_mapping, environment=env)
        if not result or not result.id:
            message = f"Failed to deploy '{image}' service on host: {service_data.host}"
            logger.exception(message)
            raise RuntimeError(message)
        service_data.pid = result.id
        client.close()

    @staticmethod
    def stop_docker_service(logger: Logger, service_data: Union[DataMongoDB, DataRabbitMQ]) -> None:
        if not service_data.pid:
            logger.warning("No running service found")
            return
        client = create_docker_client(
            service_data.host, service_data.ssh_username, service_data.ssh_password, service_data.ssh_keypath
        )
        client.containers.get(service_data.pid).stop()
        client.close()


class DataMongoDB(DataNetworkService):
    def __init__(
        self, host: str, port: int, ssh_username: Optional[str], ssh_keypath: Optional[str],
        ssh_password: Optional[str], cred_username: Optional[str], cred_password: Optional[str],
        skip_deployment: bool, protocol: str = "mongodb"
    ) -> None:
        service_url = f"{protocol}://{host}:{port}"
        if cred_username and cred_password:
            service_url = f"{protocol}://{cred_username}:{cred_password}@{host}:{port}"
        super().__init__(
            host=host, port=port, ssh_username=ssh_username, ssh_keypath=ssh_keypath, ssh_password=ssh_password,
            cred_username=cred_username, cred_password=cred_password, service_url=service_url,
            skip_deployment=skip_deployment, pid=None
        )

    def deploy_mongodb(
        self, logger: Logger, image: str = DOCKER_IMAGE_MONGO_DB, detach: bool = True, remove: bool = True,
        env: Optional[List[str]] = None, ports_mapping: Optional[Dict] = None
    ) -> str:
        if self.skip_deployment:
            logger.debug("MongoDB is managed externally. Skipping deployment.")
            verify_mongodb_available(self.service_url)
            return self.service_url
        if not env:
            env = []
            if self.cred_username:
                env = [
                    f"MONGO_INITDB_ROOT_USERNAME={self.cred_username}",
                    f"MONGO_INITDB_ROOT_PASSWORD={self.cred_password}"
                ]
        if not ports_mapping:
            ports_mapping = {27017: self.port}
        self.deploy_docker_service(logger, self, image, env, ports_mapping, detach, remove)
        verify_mongodb_available(self.service_url)
        mongodb_host_info = f"{self.host}:{self.port}"
        logger.info(f"The MongoDB was deployed on host: {mongodb_host_info}")
        return self.service_url

    def stop_service_mongodb(self, logger: Logger) -> None:
        if self.skip_deployment:
            return
        logger.info("Stopping the MongoDB service...")
        self.stop_docker_service(logger, service_data=self)
        self.pid = None
        logger.info("The MongoDB service is stopped")


class DataRabbitMQ(DataNetworkService):
    def __init__(
        self, host: str, port: int, ssh_username: Optional[str], ssh_keypath: Optional[str],
        ssh_password: Optional[str], cred_username: Optional[str], cred_password: Optional[str],
        skip_deployment: bool, protocol: str = "amqp", vhost: str = "/"
    ) -> None:
        self.vhost = f"/{vhost}" if vhost != "/" else vhost
        service_url = f"{protocol}://{host}:{port}{self.vhost}"
        if cred_username and cred_password:
            service_url = f"{protocol}://{cred_username}:{cred_password}@{host}:{port}{self.vhost}"
        super().__init__(
            host=host, port=port, ssh_username=ssh_username, ssh_keypath=ssh_keypath, ssh_password=ssh_password,
            cred_username=cred_username, cred_password=cred_password, service_url=service_url,
            skip_deployment=skip_deployment, pid=None
        )

    def deploy_rabbitmq(
        self, logger: Logger, image: str = DOCKER_IMAGE_RABBIT_MQ, detach: bool = True, remove: bool = True,
        env: Optional[List[str]] = None, ports_mapping: Optional[Dict] = None
    ) -> str:
        rmq_host, rmq_port, rmq_vhost = self.host, int(self.port), self.vhost
        rmq_user, rmq_password = self.cred_username, self.cred_password
        if self.skip_deployment:
            logger.debug(f"RabbitMQ is managed externally. Skipping deployment.")
            verify_rabbitmq_available(logger=logger, rabbitmq_address=self.service_url)
            return self.service_url
        if not env:
            env = [
                # The default credentials to be used by the processing workers
                f"RABBITMQ_DEFAULT_USER={rmq_user}",
                f"RABBITMQ_DEFAULT_PASS={rmq_password}",
                # These feature flags are required by default to use the newer version
                f"RABBITMQ_FEATURE_FLAGS={DOCKER_RABBIT_MQ_FEATURES}"
            ]
        if not ports_mapping:
            # 5672, 5671 - used by AMQP 0-9-1 and AMQP 1.0 clients without and with TLS
            # 15672, 15671: HTTP API clients, management UI and rabbitmq admin, without and with TLS
            # 25672: used for internode and CLI tools communication and is allocated from
            # a dynamic range (limited to a single port by default, computed as AMQP port + 20000)
            ports_mapping = {5672: self.port, 15672: 15672, 25672: 25672}
        self.deploy_docker_service(logger, self, image, env, ports_mapping, detach, remove)
        verify_rabbitmq_available(logger=logger, rabbitmq_address=self.service_url)
        logger.info(f"The RabbitMQ server was deployed on host: {rmq_host}:{rmq_port}{rmq_vhost}")
        return self.service_url

    def stop_service_rabbitmq(self, logger: Logger) -> None:
        if self.skip_deployment:
            return
        logger.info("Stopping the RabbitMQ service...")
        self.stop_docker_service(logger, service_data=self)
        self.pid = None
        logger.info("The RabbitMQ service is stopped")
