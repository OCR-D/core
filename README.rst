pyOCR-D
=======

    Collection of OCR-related python tools and wrappers from the OCR-D team

Installation
------------

To bootstrap the tool, you'll need installed (Ubuntu packages):

* Python 3 (``python3``)
* pip (``python3-pip``)
* Tesseract 3.04 headers (``libtesseract-dev``)
* Tesseract 3.04 languages (``tesseract-ocr-{eng,deu,deu-frak}``)
* Leptonica headers (``libleptonica-dev``)
* exiftool (``libimage-exiftool-perl``)

To install system-wide:

::

    pip3 install -r requirements.txt
    python3 setup.py install

To install to user HOME dir

::

    pip3 install --user -r requirements.txt
    python setup.py install --user

If tesserocr fails to compile with an error:::

    $PREFIX/include/tesseract/unicharset.h:241:10: error: ‘string’ does not name a type; did you mean ‘stdin’? 
           static string CleanupString(const char* utf8_str) {
                  ^~~~~~
                  stdin

This is due to some inconsistencies in the installed tesseract C headers. Replace ``string`` with ``std::string`` in ``$PREFIX/include/tesseract/unicharset.h:265:5:`` and ``$PREFIX/include/tesseract/unichar.h:164:10:`` ff.

If tesserocr fails with an error about ``LSTM``/``CUBE``, you are using th 4.00
headers. Downgrade to 3.04: ``apt install libtesseract-dev=3.04.01-6`` or
whatever ``apt policy libtesseract-dev`` offers. Make sure there are no spurious pkg-config artifacts, e.g. in ``/usr/local/lib/pkgconfig/tesseract.pc``. The same goes for language models



See Also
--------

* `OCR-D Specifications <https://github.com/ocr-d/spec>`_
