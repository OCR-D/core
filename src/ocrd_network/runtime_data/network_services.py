from __future__ import annotations
from logging import Logger
from typing import Any, Dict, List, Optional, Union

from ..constants import DOCKER_IMAGE_MONGO_DB, DOCKER_IMAGE_RABBIT_MQ, DOCKER_RABBIT_MQ_FEATURES
from ..utils import verify_mongodb_available, verify_rabbitmq_available
from .connection_clients import create_docker_client


class DataNetworkService:
    def __init__(
        self,
        host: str,
        port: int,
        ssh: Dict,
        credentials: Dict,
        service_url: str,
        skip_deployment: bool,
        pid: Optional[Any]
    ) -> None:
        self.host = host
        self.port = port
        self.ssh_username = ssh.get("username", None)
        self.ssh_keypath = ssh.get("path_to_privkey", None)
        self.ssh_password = ssh.get("password", None)
        self.cred_username = credentials.get("username", None)
        self.cred_password = credentials.get("password", None)
        self.service_url = service_url
        self.skip_deployment = skip_deployment
        self.pid = pid

    @staticmethod
    def deploy_docker_service(
        logger: Logger,
        service_data: Union[DataMongoDB, DataRabbitMQ],
        image: str,
        env: Optional[List[str]],
        ports_mapping: Optional[Dict],
        detach: bool = True,
        remove: bool = True
    ) -> None:
        if not service_data or not service_data.host:
            message = f"Deploying '{image}' has failed - missing service configurations."
            logger.exception(message)
            raise RuntimeError(message)
        logger.info(f"Deploying '{image}' service on '{service_data.host}', detach={detach}, remove={remove}")
        logger.info(f"Ports mapping: {ports_mapping}")
        logger.info(f"Environment: {env}")
        client = create_docker_client(
            service_data.host,
            service_data.ssh_username,
            service_data.ssh_password,
            service_data.ssh_keypath
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
        client = create_docker_client(
            service_data.host,
            service_data.ssh_username,
            service_data.ssh_password,
            service_data.ssh_keypath
        )
        client.containers.get(service_data.pid).stop()
        client.close()


class DataMongoDB(DataNetworkService):
    def __init__(self, config: Dict, protocol: str = "mongodb") -> None:
        host = config["address"]
        port = int(config["port"])
        ssh_dict = {}
        if "ssh" in config:
            ssh_dict = config["ssh"]
        credentials_dict = {}
        if "credentials" in config:
            credentials_dict = config["credentials"]
            username, password = credentials_dict["username"], credentials_dict["password"]
            service_url = f"{protocol}://{username}:{password}@{host}:{port}"
        else:
            service_url = f"{protocol}://{host}:{port}"
        super().__init__(
            host=host,
            port=port,
            ssh=ssh_dict,
            credentials=credentials_dict,
            service_url=service_url,
            skip_deployment=config.get("skip_deployment", False),
            pid=None
        )

    def deploy_mongodb(
        self,
        logger: Logger,
        image: str = DOCKER_IMAGE_MONGO_DB,
        detach: bool = True,
        remove: bool = True,
        env: Optional[List[str]] = None,
        ports_mapping: Optional[Dict] = None
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
            ports_mapping = {
                27017: self.port
            }
        self.deploy_docker_service(logger, self, image, env, ports_mapping, detach, remove)
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
    def __init__(self, config: Dict, protocol: str = "amqp", vhost: str = "/") -> None:
        host = config["address"]
        port = int(config["port"])
        self.vhost = vhost
        ssh_dict = {}
        if "ssh" in config:
            ssh_dict = config["ssh"]
        credentials_dict = {}
        if "credentials" in config:
            credentials_dict = config["credentials"]
            username, password = credentials_dict["username"], credentials_dict["password"]
            service_url = f"{protocol}://{username}:{password}@{host}:{port}{self.vhost}"
        else:
            service_url = f"{protocol}://{host}:{port}{self.vhost}"
        super().__init__(
            host=host,
            port=port,
            ssh=ssh_dict,
            credentials=credentials_dict,
            service_url=service_url,
            skip_deployment=config.get("skip_deployment", False),
            pid=None
        )

    def deploy_rabbitmq(
        self,
        logger: Logger,
        image: str = DOCKER_IMAGE_RABBIT_MQ,
        detach: bool = True,
        remove: bool = True,
        env: Optional[List[str]] = None,
        ports_mapping: Optional[Dict] = None
    ) -> str:
        rmq_host, rmq_port, rmq_vhost = self.host, int(self.port), self.vhost
        rmq_user, rmq_password = self.cred_username, self.cred_password
        if self.skip_deployment:
            logger.debug(f"RabbitMQ is managed externally. Skipping deployment.")
            # Testing the UI front end running on port 15672
            verify_rabbitmq_available(rmq_host, 15672, rmq_vhost, rmq_user, rmq_password)
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
            ports_mapping = {
                5672: self.port,
                15672: 15672,
                25672: 25672
            }
        self.deploy_docker_service(logger, self, image, env, ports_mapping, detach, remove)
        # Testing the UI front end running on port 15672
        verify_rabbitmq_available(rmq_host, 15672, rmq_vhost, rmq_user, rmq_password)
        logger.info(f"The RabbitMQ server was deployed on host: {rmq_host}:{rmq_port}{rmq_vhost}")
        return self.service_url

    def stop_service_rabbitmq(self, logger: Logger) -> None:
        if self.skip_deployment:
            return
        logger.info("Stopping the RabbitMQ service...")
        self.stop_docker_service(logger, service_data=self)
        self.pid = None
        logger.info("The RabbitMQ service is stopped")
