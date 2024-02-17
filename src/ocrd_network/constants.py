DOCKER_IMAGE_MONGO_DB = "mongo"
DOCKER_IMAGE_RABBIT_MQ = "rabbitmq:3.12-management"
# These feature flags are required by default to use the newer version
DOCKER_RABBIT_MQ_FEATURES = "quorum_queue,implicit_default_bindings,classic_mirrored_queue_version"

NETWORK_API_TAG_ADMIN = "admin"
NETWORK_API_TAG_DISCOVERY = "discovery"
NETWORK_API_TAG_PROCESSING = "processing"
NETWORK_API_TAG_TOOLS = "tools"
NETWORK_API_TAG_WORKFLOW = "workflow"
NETWORK_API_TAG_WORKSPACE = "workspace"

NETWORK_AGENT_SERVER = "server"
NETWORK_AGENT_WORKER = "worker"
NETWORK_AGENT_TYPES = [NETWORK_AGENT_SERVER, NETWORK_AGENT_WORKER]

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


