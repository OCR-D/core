# BEGIN-EVAL makefile-parser --make-help Makefile

help:
	@echo ""
	@echo "  Targets"
	@echo ""
	@echo "    lib        Build the lib"
	@echo "    watch-lib  Continuously build lib"
	@echo "    doc        Include the docs from the README"

# END-EVAL

# Build the lib
lib: lib.bash

.DELETE_ON_ERROR:
lib.bash: $(wildcard src/*.bash)
	shinclude -c pound src/lib.bash > "$@"

# Continuously build lib
watch-lib:
	nodemon -w src -e bash -x make lib

# Include the docs from the README
doc: README.md

README.md: lib.bash
	shinclude -c xml -i README.md
