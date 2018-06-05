core
====


    Collection of OCR-related python tools and wrappers from the OCR-D team

.. image:: https://travis-ci.org/OCR-D/core.svg?branch=master
    :target: https://travis-ci.org/OCR-D/core

.. image:: https://img.shields.io/docker/automated/ocrd/pyocrd.svg
    :target: https://hub.docker.com/r/ocrd/core/tags/
    :alt: Docker Automated build

.. image:: https://img.shields.io/pypi/v/ocrd.svg
    :target: https://pypi.org/project/ocrd/

Installation
------------

To bootstrap the tool, you'll need installed (Ubuntu packages):

* Python (``python``)
* pip (``python-pip``)
* exiftool (``libimage-exiftool-perl``)
* libxml2-utils for xmllint (``libxml2-utils``)

To install system-wide:

::

    make deps-ubuntu deps-pip install


To develop, install to a virtualenv

::

    pip install virtualenv
    virtualenv --no-site-packages venv
    source venv/bin/activate
    make deps-pip install

Usage
-----

pyocrd installs a binary ``ocrd`` that can be used to invoke the processors
directly (``ocrd process``) or start (development) webservices (``ocrd server``)

**TODO**: Update docs here.

Examples:

::

    # List available processors
    ocrd process

    # Region-segment with tesserocr all files in METS INPUT fileGrp
    ocrd process -m /path/to/mets.xml segment-region/tesserocr

    # Chain multiple processors
    ocrd process -m /path/to/mets.xml characterize/exif segment-line/tesserocr recognize/tesserocr

    # Start a processor web service at port 6543
    ocrd server process -p 6543
    http PUT localhost:6543/characterize url==http://server/path/to/mets.xml

Testing
-------

Download assets (``make assets``)

Test with local files: ``make test``

Test with local asset server:
  - Start asset-server: ``make asset-server``
  - ``make test OCRD_BASEURL='http://localhost:5001/'``

Test with remote assets:
  - ``make test OCRD_BASEURL='https://github.com/OCR-D/assets/raw/master/data/'``

See Also
--------

* `OCR-D Specifications <https://github.com/ocr-d/spec>`_
* `pyocrd wiki <https://github.com/ocr-d/pyocrd/wiki>`_
