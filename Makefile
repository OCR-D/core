# BEGIN-EVAL makefile-parser --make-help Makefile

help:
	@echo ""
	@echo "  Targets"
	@echo ""
	@echo "    deps-ubuntu  Dependencies for deployment in an ubuntu/debian linux"
	@echo "    deps-pip     Install python deps via pip"
	@echo "    spec         Clone the spec dir for sample files"
	@echo "    install      (Re)install the tool"
	@echo "    test-run     Test the run command"

# END-EVAL

# Dependencies for deployment in an ubuntu/debian linux
deps-ubuntu:
	apt install python3 python3-pip libtesseract-dev libleptonica-dev libimage-exiftool-perl

# Install python deps via pip
deps-pip:
	pip3 install --user -r requirements.txt

# Clone the spec dir for sample files
spec:
	git clone https://github.com/OCR-D/spec

# (Re)install the tool
install:
	pip3 install --user .

# Test the run command
test-run: spec
	run-ocrd spec/io/example/mets.xml
