from pathlib import Path
from tempfile import gettempdir
from ocrd_utils.config import OcrdEnvConfig
from ocrd_utils.config import _ocrd_download_timeout_parser

test_config = OcrdEnvConfig()

test_config.add(
    name='OCRD_METS_CACHING',
    description='If set to `true`, access to the METS file is cached, speeding in-memory search and modification.',
    validator=lambda val: val in ('true', 'false', '0', '1'),
    parser=lambda val: val in ('true', '1')
)

test_config.add(
    name='OCRD_MAX_PROCESSOR_CACHE',
    description="""
    Maximum number of processor instances (for each set of parameters) to be kept in memory (including loaded models) 
    for processing workers or processor servers.
    """,
    parser=int,
    default=(True, 128)
)

test_config.add(
    name='OCRD_PROFILE',
    description="""
    Whether to enable gathering runtime statistics
    on the `ocrd.profile` logger (comma-separated):
    - `CPU`: yields CPU and wall-time,
    - `RSS`: also yields peak memory (resident set size)
    - `PSS`: also yields peak memory (proportional set size)
    """,
    validator=lambda val: all(t in ('', 'CPU', 'RSS', 'PSS') for t in val.split(',')),
    default=(True, '')
)

test_config.add(
    name="OCRD_PROFILE_FILE",
    description="""
    If set, then the CPU profile is written to this file for later peruse with a analysis tools like snakeviz
    """
)

test_config.add(
    name="OCRD_DOWNLOAD_RETRIES",
    description="Number of times to retry failed attempts for downloads of workspace files.",
    validator=int,
    parser=int,
)

test_config.add(
    name="OCRD_DOWNLOAD_TIMEOUT",
    description="Timeout in seconds for connecting or reading (comma-separated) when downloading.",
    parser=_ocrd_download_timeout_parser
)

test_config.add(
    "OCRD_NETWORK_CLIENT_POLLING_SLEEP",
    description="How many seconds to sleep before trying again.",
    parser=int,
    default=(True, 30)
)

test_config.add(
    "OCRD_NETWORK_CLIENT_POLLING_TIMEOUT",
    description="Timeout for a blocking ocrd network client (in seconds).",
    parser=int,
    default=(True, 3600)
)

test_config.add(
    name="OCRD_NETWORK_SERVER_ADDR_PROCESSING",
    description="Default address of Processing Server to connect to (for `ocrd network client processing`).",
    default=(True, '')
)

test_config.add(
    name="OCRD_NETWORK_SERVER_ADDR_WORKFLOW",
    description="Default address of Workflow Server to connect to (for `ocrd network client workflow`).",
    default=(True, '')
)

test_config.add(
    name="OCRD_NETWORK_SERVER_ADDR_WORKSPACE",
    description="Default address of Workspace Server to connect to (for `ocrd network client workspace`).",
    default=(True, '')
)

test_config.add(
    name="OCRD_NETWORK_RABBITMQ_CLIENT_CONNECT_ATTEMPTS",
    description="Number of attempts for a RabbitMQ client to connect before failing",
    parser=int,
    default=(True, 3)
)

test_config.add(
    name="OCRD_NETWORK_RABBITMQ_HEARTBEAT",
    description="""
    Controls AMQP heartbeat timeout (in seconds) negotiation during connection tuning. An integer value always overrides the value 
    proposed by broker. Use 0 to deactivate heartbeat.
    """,
    parser=int,
    default=(True, 0)
)

test_config.add(
    name="OCRD_NETWORK_SOCKETS_ROOT_DIR",
    description="The root directory where all mets server related socket files are created",
    parser=lambda val: Path(val),
    default=(True, Path(gettempdir(), "ocrd_network_sockets"))
)
test_config.OCRD_NETWORK_SOCKETS_ROOT_DIR.mkdir(parents=True, exist_ok=True)
# Remove socket files left from previous integration tests
for path in test_config.OCRD_NETWORK_SOCKETS_ROOT_DIR.iterdir():
    if path.is_socket() and path.suffix == '.sock':
        path.unlink()

test_config.add(
    name="OCRD_NETWORK_LOGS_ROOT_DIR",
    description="The root directory where all ocrd_network related file logs are stored",
    parser=lambda val: Path(val),
    default=(True, Path(gettempdir(), "ocrd_network_logs"))
)
test_config.OCRD_NETWORK_LOGS_ROOT_DIR.mkdir(parents=True, exist_ok=True)

test_config.add(
    name="HOME",
    description="Directory to look for `ocrd_logging.conf`, fallback for unset XDG variables.",
    # description="HOME directory, cf. https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html",
    validator=lambda val: Path(val).is_dir(),
    parser=lambda val: Path(val),
    default=(True, lambda: Path.home())
)

test_config.add(
    name="XDG_DATA_HOME",
    description="Directory to look for `./ocrd/resources.yml` (i.e. `ocrd resmgr` user database)",
    parser=lambda val: Path(val),
    default=(True, lambda: Path(test_config.HOME, '.local/share'))
)

test_config.add(
    name="XDG_CONFIG_HOME",
    description="Directory to look for `./ocrd-resources/*` (i.e. `ocrd resmgr` data location)",
    parser=lambda val: Path(val),
    default=(True, lambda: Path(test_config.HOME, '.config'))
)

test_config.add(
    name="OCRD_LOGGING_DEBUG",
    description="Print information about the logging setup to STDERR",
    default=(True, False),
    validator=lambda val: isinstance(val, bool) or val in ('true', 'false', '0', '1'),
    parser=lambda val:  val in ('true', '1')
)
