deps-ubuntu:
	apt install python3 python3-pip libtesseract-dev libleptonica-dev libimage-exiftool-perl

spec:
	git clone https://github.com/OCR-D/spec

test-install:
	pip3 install --user -r requirements.txt

test-run: spec
	run-ocrd spec/io/example/mets.xml
