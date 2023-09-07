WG_ENV := wg_env

# install latest version from https://github.com/lindenb/makefile2graph to get mermaid mode
MAKE2GRAPH := ~/Software/makefile2graph/make2graph

install: $(WG_ENV)

configure:
	. $(WG_ENV)/bin/activate

store_configuration: configure
	pip freeze > requirements.txt

$(WG_ENV): requirements.txt
	virtualenv $(WG_ENV)
	$(WG_ENV)/bin/pip install -r requirements.txt

dependencies.mmd: Makefile
	make -Bnd | $(MAKE2GRAPH) --format m > dependencies.mmd
