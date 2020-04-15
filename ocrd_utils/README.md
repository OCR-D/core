# ocrd_utils

> OCR-D framework - shared code, helpers, constants

See https://github.com/OCR-D/core


## OCR-D Module Logging

File-based control over logging facilities is done with standard [Python 3 logging module configuration files](https://docs.python.org/3.6/howto/logging.html#configuring-logging). This way, the level, format and destinations of log messages can be customized for all OCR-D modules individually and persistently, in the usual syntax.

A template configuration file (with commented examples) is included in [ocrd_logging.conf](./ocrd_logging.conf). This is meant as an example, and should be **customized**. 

To get into effect, you must put a copy (under the same name) into:
1. your current working directory, 
2. your user directory, or
3. `/etc`. 
These directories are searched in said order, and the first find wins. When no config file is found, the default logging configuration applies (which uses only stdout and the `INFO` loglevel for most loggers, cf. [here](./ocrd_logging.py)).

Thus, a configuration file will override *all* settings from the default configuration, and from configuration files in lower-priority directories.

For more information about logging, handlers and formats, see [Python documentation](https://docs.python.org/3/howto/logging.htm).

#### Docker containers

In the Dockerfiles used to build `ocrd/core` (and subsequently `ocrd/all`), the above mentioned template is directly copied to `/etc/ocrd_logging.conf` within the container image. This cofiguration is thereby also the default configuration for OCR-D containers. 

Thus, if you want to customize logging rules in one of these Docker containers, you can create a custom configuration file and either:
- place it into your local workspace directory when running the OCR-D container.
- mount it under `/etc` when starting up the container, e.g. `docker run --mount type=bind,source=host/path/to/your-template.conf,destination=/etc/ocrd_logging.conf ocrd/all`
- include a Dockerfile step (layer or stage) which copies this into `/etc/ocrd_logging.conf` at build time in your own Docker image.
