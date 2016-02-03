build:
	python setup.py build

install:
	python setup.py install

clear:
	rm -vrf ./build ./dist ./*.tgz ./*.egg-info ./.cache ./.tox
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf

pep8:
	pep8 --show-source

test:
	tox

.PHONY: build
