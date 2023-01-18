.PHONY: all
PYTHON = python3
OO = -OO
INSTALLER = PyInstaller
ENTRY = vidgetter.py
OPTS = --onefile --strip

all: dist

dist:
	${PYTHON} ${OO} -m ${INSTALLER} ${ENTRY} ${OPTS}

clean:
	rm -rfv build dist vidgetter.spec
