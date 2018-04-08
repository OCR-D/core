pyocrd
======


    Collection of OCR-related python tools and wrappers from the OCR-D team

.. image:: https://travis-ci.org/OCR-D/pyocrd.svg?branch=master
    :target: https://travis-ci.org/OCR-D/pyocrd

.. image:: https://img.shields.io/docker/automated/ocrd/pyocrd.svg
    :target: https://hub.docker.com/r/ocrd/pyocrd/tags/
    :alt: Docker Automated build

Installation
------------

To bootstrap the tool, you'll need installed (Ubuntu packages):

* Python (``python``)
* pip (``python-pip``)
* exiftool (``libimage-exiftool-perl``)
* libxml2-utils for xmllint (``libxml2-utils``)

To install system-wide:

::

    sudo make deps-ubuntu
    pip install -r requirements.txt
    pip install .

To install to user HOME dir

::

    sudo make deps-ubuntu
    pip install --user -r requirements.txt
    pip install .

To develop, install to a virtualenv

::

    pip install virtualenv
    virtualenv --no-site-packages venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install .

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

Download ocrd-assets (``make assets``)

Test with local files: ``make test``

Test with local asset server:
  - Start asset-server: ``make asset-server``
  - ``OCRD_BASEURL='http://localhost:5001/' make test``

Test with remote assets:
  - ``OCRD_BASEURL='https://github.com/OCR-D/ocrd-assets/raw/master/data/' make test``

See Also
--------

* `OCR-D Specifications <https://github.com/ocr-d/spec>`_
* `pyocrd wiki <https://github.com/ocr-d/pyocrd/wiki>`_
