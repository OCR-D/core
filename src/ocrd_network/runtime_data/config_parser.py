from typing import Any, Dict, List
from yaml import safe_load

from ocrd_validators import ProcessingServerConfigValidator
from .hosts import DataHost
from .network_services import DataMongoDB, DataRabbitMQ


def validate_and_load_config(config_path: str) -> Dict[str, Any]:
    # Load and validate the config
    with open(config_path) as fin:
        ps_config = safe_load(fin)
    report = ProcessingServerConfigValidator.validate(ps_config)
    if not report.is_valid:
        raise ValueError(f"Processing-Server configuration file is invalid:\n{report.errors}")
    return ps_config


def _parse_network_service_config(config: Dict[str, Any]) -> Dict[str, Any]:
    ssh = config.get("ssh", {})
    credentials = config.get("credentials", {})
    return {
        "host": config["address"],
        "port": int(config["port"]),
        "ssh_username": ssh.get("username"),
        "ssh_keypath": ssh.get("path_to_privkey"),
        "ssh_password": ssh.get("password"),
        "cred_username": credentials.get("username"),
        "cred_password": credentials.get("password"),
        "skip_deployment": config.get("skip_deployment", False)
    }


# Parse MongoDB data from the Processing Server configuration file
def parse_mongodb_data(db_config: Dict[str, Any]) -> DataMongoDB:
    return DataMongoDB(**_parse_network_service_config(db_config))


# Parse RabbitMQ data from the Processing Server configuration file
def parse_rabbitmq_data(rmq_config: Dict[str, Any]) -> DataRabbitMQ:
    return DataRabbitMQ(**_parse_network_service_config(rmq_config))


def parse_hosts_data(hosts_config: List[Dict[str, Any]]) -> List[DataHost]:
    hosts_data: List[DataHost] = []
    for host_config in hosts_config:
        hosts_data.append(
            DataHost(
                host=host_config["address"], username=host_config["username"],
                password=host_config.get("password", None), keypath=host_config.get("path_to_privkey", None),
                workers=host_config.get("workers", []), servers=host_config.get("servers", [])
            )
        )
    return hosts_data
