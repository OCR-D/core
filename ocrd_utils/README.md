# ocrd_utils

Additional functionalities for OCR-D framework

See https://github.com/OCR-D/core


## OCR-D Module Logging

_Please note, that the following instructions only apply to the dockerized version of `ocrd_utils`._

Configuration of Logging-Facilities is done with standard Python3 Logging Library from modul `logging`. This way, logging configuration can be customized for all OCR-D modules using the Python logging framework.  
A sample configuration file is included in the OCR-D container image at `/etc/ocrd_logging.conf`. This cofiguration is also meant to be the default configuration for OCR-D container images.  
If this file doesn't exist or gets removed, logging mechanics use as fallback the `logging.basicConfig` functionalities which use stdout as message channel. 

For more information about logging, handlers and formats, please see https://docs.python.org/3/howto/logging.htm.

### Customization

Create a custom Configuration and include this as part of your local workspace when running the OCR-D container.  
In this case, it will override *all* settings from default configuration, which is included at `/etc/ocrd_logging.conf`.  
