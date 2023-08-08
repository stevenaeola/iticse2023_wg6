WG_ENV := wg_env
WD := $(shell pwd)

install: $(WG_ENV)

configure:
	. $(WG_ENV)/bin/activate

store_configuration: configure
	pip freeze > requirements.txt


$(WG_ENV): requirements.txt
	virtualenv $(WG_ENV)
	$(WG_ENV)/bin/pip install -r requirements.txt

