export

SHELL = /bin/bash
PYTHONPATH := .:$(PYTHONPATH)

# BEGIN-EVAL makefile-parser --make-help Makefile

help:
	@echo ""
	@echo "  Targets"
	@echo ""
	@echo "    deps-ubuntu  Dependencies for deployment in an ubuntu/debian linux"
	@echo "    deps-pip     Install python deps via pip"
	@echo "    spec         Clone the spec dir for sample files"
	@echo "    install      (Re)install the tool"
	@echo "    test         Run all unit tests"

# END-EVAL

# Dependencies for deployment in an ubuntu/debian linux
deps-ubuntu:
	apt install \
		python3 \
		python3-pip \
		libtesseract-dev \
		libleptonica-dev \
		libimage-exiftool-perl \
		tesseract-ocr-eng \
		tesseract-ocr-deu \
		tesseract-ocr-deu-frak

# Install python deps via pip
deps-pip:
	pip3 install --user -r requirements.txt

# Clone the spec dir for sample files
spec:
	git clone https://github.com/OCR-D/spec

# (Re)install the tool
install:
	pip3 install --user .

test/assets: spec
	mkdir -p test/assets
	cp -r spec/io/example test/assets/herold

.PHONY: test
# Run all unit tests
test:
	@for t in test/*.test.py; do\
	    echo -e "# ***\n# *** Testing $$t\n# ***";\
	    python $$t;\
	done

