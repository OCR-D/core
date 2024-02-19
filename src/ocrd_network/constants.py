from enum import Enum

DOCKER_IMAGE_MONGO_DB = "mongo"
DOCKER_IMAGE_RABBIT_MQ = "rabbitmq:3.12-management"
# These feature flags are required by default to use the newer version
DOCKER_RABBIT_MQ_FEATURES = "quorum_queue,implicit_default_bindings,classic_mirrored_queue_version"

NETWORK_PROTOCOLS = ["http://", "https://"]
OCRD_ALL_JSON_TOOLS_URL = "https://ocr-d.de/js/ocrd-all-tool.json"
OCRD_NETWORK_MODULES = [
    "mets_servers",
    "processing_jobs",
    "processing_servers",
    "processing_workers",
    "processor_servers"
]
SERVER_ALL_PAGES_PLACEHOLDER = "all_pages"


class AgentType(str, Enum):
    PROCESSING_WORKER = "worker"
    PROCESSOR_SERVER = "server"


class DeployType(str, Enum):
    # Deployed by the Processing Server config file
    DOCKER = "docker"
    NATIVE = "native"
    # Deployed through a registration endpoint of the Processing Server
    # TODO: That endpoint is still not implemented
    EXTERNAL = "external"


# TODO: Make the states uppercase
class JobState(str, Enum):
    # The processing job is cached inside the Processing Server requests cache
    cached = "CACHED"
    # The processing job was cancelled due to failed dependencies
    cancelled = "CANCELLED"
    # Processing job failed
    failed = "FAILED"
    # The processing job is queued inside the RabbitMQ
    queued = "QUEUED"
    # Processing job is currently running in a Worker or Processor Server
    running = "RUNNING"
    # Processing job finished successfully
    success = "SUCCESS"
    # Processing job has not been assigned yet
    unset = "UNSET"


class ServerApiTags(str, Enum):
    ADMIN = "admin"
    DISCOVERY = "discovery"
    PROCESSING = "processing"
    TOOLS = "tools"
    WORKFLOW = "workflow"
    WORKSPACE = "workspace"
