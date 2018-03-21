pyOCR-D
=======

    Collection of OCR-related python tools and wrappers from the OCR-D team

Installation
------------

To bootstrap the tool, you'll need installed (Ubuntu packages):

* Python (``python``)
* pip (``python-pip``)
* Tesseract (3.04) headers (``libtesseract-dev``)
* Some tesseract (3.04) language models (``tesseract-ocr-{eng,deu,deu-frak,...}``)
* Leptonica headers (``libleptonica-dev``)
* exiftool (``libimage-exiftool-perl``)

To install system-wide:

::

    pip install -r requirements.txt
    pip install .

To install to user HOME dir

::

    pip install --user -r requirements.txt
    pip install .

To develop, install to a virtulenv

::

    pip install virtualenv
    virtualenv --no-site-packages venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install .

If tesserocr fails to compile with an error:::

    $PREFIX/include/tesseract/unicharset.h:241:10: error: ‘string’ does not name a type; did you mean ‘stdin’? 
           static string CleanupString(const char* utf8_str) {
                  ^~~~~~
                  stdin

This is due to some inconsistencies in the installed tesseract C headers. Replace ``string`` with ``std::string`` in ``$PREFIX/include/tesseract/unicharset.h:265:5:`` and ``$PREFIX/include/tesseract/unichar.h:164:10:`` ff.

If tesserocr fails with an error about ``LSTM``/``CUBE``, you are using th 4.00
headers. Downgrade to 3.04: ``apt install libtesseract-dev=3.04.01-6`` or
whatever ``apt policy libtesseract-dev`` offers. Make sure there are no spurious pkg-config artifacts, e.g. in ``/usr/local/lib/pkgconfig/tesseract.pc``. The same goes for language models


Usage
-----

::

    run-ocrd <METS-FILE>

This will run the image characterization, page segmentation and region segmentation.

See Also
--------

* `OCR-D Specifications <https://github.com/ocr-d/spec>`_
