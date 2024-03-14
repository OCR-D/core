from typing import Dict, List
from yaml import safe_load

from ocrd_validators import ProcessingServerConfigValidator
from .hosts import DataHost
from .network_services import DataMongoDB, DataRabbitMQ


def validate_and_load_config(config_path: str) -> Dict:
    # Load and validate the config
    with open(config_path) as fin:
        ps_config = safe_load(fin)
    report = ProcessingServerConfigValidator.validate(ps_config)
    if not report.is_valid:
        raise Exception(f"Processing-Server configuration file is invalid:\n{report.errors}")
    return ps_config


# Parse MongoDB data from the Processing Server configuration file
def parse_mongodb_data(db_config: Dict) -> DataMongoDB:
    db_ssh = db_config.get("ssh", {})
    db_credentials = db_config.get("credentials", {})
    return DataMongoDB(
        host=db_config["address"], port=int(db_config["port"]), ssh_username=db_ssh.get("username", None),
        ssh_keypath=db_ssh.get("path_to_privkey", None), ssh_password=db_ssh.get("password", None),
        cred_username=db_credentials.get("username", None), cred_password=db_credentials.get("password", None),
        skip_deployment=db_config.get("skip_deployment", False)
    )


# Parse RabbitMQ data from the Processing Server configuration file
def parse_rabbitmq_data(rmq_config: Dict) -> DataRabbitMQ:
    rmq_ssh = rmq_config.get("ssh", {})
    rmq_credentials = rmq_config.get("credentials", {})
    return DataRabbitMQ(
        host=rmq_config["address"], port=int(rmq_config["port"]), ssh_username=rmq_ssh.get("username", None),
        ssh_keypath=rmq_ssh.get("path_to_privkey", None), ssh_password=rmq_ssh.get("password", None),
        cred_username=rmq_credentials.get("username", None), cred_password=rmq_credentials.get("password", None),
        skip_deployment=rmq_config.get("skip_deployment", False)
    )


def parse_hosts_data(hosts_config: Dict) -> List[DataHost]:
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
