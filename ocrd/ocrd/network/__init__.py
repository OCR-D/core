# This network package is supposed to contain all the packages and modules to realize the network architecture:
# https://user-images.githubusercontent.com/7795705/203554094-62ce135a-b367-49ba-9960-ffe1b7d39b2c.jpg

# For reference, currently:
# 1. The WebAPI is available here:
# https://github.com/OCR-D/ocrd-webapi-implementation
# 2. The RabbitMQ Library (i.e., utils) is available here:
# https://github.com/OCR-D/ocrd-webapi-implementation/tree/main/ocrd_webapi/rabbitmq
# 3. Some potentially more useful code to be adopted for the Processing Server/Worker is available here:
# https://github.com/OCR-D/core/pull/884
# 4. The Mets Server discussion/implementation is available here:
# https://github.com/OCR-D/core/pull/966

# Note: The Mets Server is still not placed on the architecture diagram and probably won't be a part of
# the network package. The reason, Mets Server is tightly coupled with the `OcrdWorkspace`.

# This package, currently, is under the `core/ocrd` package.
# It could also be a separate package on its own under `core` with the name `ocrd_network`.
# TODO: Correctly identify all current and potential future dependencies.
from .processing_server import ProcessingServer
from .processing_worker import ProcessingWorker
