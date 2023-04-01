# This network package is supposed to contain all the packages and modules to realize the network architecture:
# https://github.com/OCR-D/spec/pull/222/files#diff-8d0dae8c9277ff1003df93c5359c82a12d3f5c8452281f87781921921204d283

# For reference, currently:
# 1. The WebAPI is available here: https://github.com/OCR-D/ocrd-webapi-implementation
# The ocrd-webapi-implementation repo implements the Discovery / Workflow / Workspace endpoints of the WebAPI currently.
# This Processing Server PR implements just the Processor endpoint of the WebAPI. 
# Once we have this merged to core under ocrd-network, the other endpoints will be adapted to ocrd-network 
# and then the ocrd-webapi-implementation repo can be archived for reference.

# 2. The RabbitMQ Library (i.e., utils) is used as an API to abstract and 
# simplify (from the view point of processing server and workers) interactions with the RabbitMQ Server.
# The library was adopted from: https://github.com/OCR-D/ocrd-webapi-implementation/tree/main/ocrd_webapi/rabbitmq

# 3. Some potentially more useful code to be adopted for the Processing Server/Worker is available here:
# https://github.com/OCR-D/core/pull/884
# Update: Should be revisited again for adopting any relevant parts (if necessary). 
# Nothing relevant is under the radar for now.

# 4. The Mets Server discussion/implementation is available here:
# https://github.com/OCR-D/core/pull/966

# Note: The Mets Server is still not placed on the architecture diagram and probably won't be a part of
# the network package. The reason, Mets Server is tightly coupled with the `OcrdWorkspace`.
from .processing_server import ProcessingServer
from .processing_worker import ProcessingWorker
from .processor_server import ProcessorServer
from .param_validators import (
    DatabaseParamType,
    ServerAddressParamType,
    QueueServerParamType
)
