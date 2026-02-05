install:
	@pip install flit>=3.10.1
	@git clean -fd
	@flit build
	@pip install -q --force-reinstall dist/*.whl

install-test:
	@pip install -e .[tests]
	@pip install h5py
	@python -m pip install -q --force-reinstall dist/*.whl > /dev/null

version-info:
	@bash -c "date -u +'Build date: %B %d, %Y %H:%M UTC ShaID: <id>' | xargs -I date sed -i 's/_VERSION_INFO = .*/_VERSION_INFO = \"date\"/g' src/ansys/cfx/core/__init__.py"
	@bash -c "git --no-pager log -n 1 --format='%h' | xargs -I hash sed -i 's/<id>/hash/g' src/ansys/cfx/core/__init__.py"

docker-pull:
	@bash .ci/pull_cfx_image.sh

docker-clean-images:
	@docker system prune --volumes -a -f

test-import:
	@python -c "import ansys.cfx.core as pycfx"

PYTESTEXTRA = --cache-clear --cov=ansys.cfx.core --cov-report=term --cov-report=html:.cov/html --cov-report=xml:.cov/xml --cov-report=json:.cov/cov.json
PYTESTRERUN = --last-failed --last-failed-no-failures none

unittest: unittest-dev-252

unittest-dev-252:
	@echo "Running unit tests"
	@python -m pytest --cfx-version=25.2 $(PYTESTEXTRA) || python -m pytest --cfx-version=25.2 $(PYTESTRERUN)

unittest-all-252:
	@echo "Running all unit tests"
	@python -m pytest --cfx-version=25.2 $(PYTESTEXTRA) || python -m pytest --cfx-version=25.2 $(PYTESTRERUN)

unittest-all-252-no-codegen:
	@echo "Running all unit tests"
	@python -m pytest --cfx-version=25.2 -m "not codegen_required" $(PYTESTEXTRA) || python -m pytest --cfx-version=25.2 -m "not codegen_required" $(PYTESTRERUN)

unittest-dev-261:
	@echo "Running unit tests"
	@poetry run python -m pytest --cfx-version=26.1 $(PYTESTEXTRA) || poetry run python -m pytest --cfx-version=26.1 $(PYTESTRERUN)

unittest-all-261:
	@echo "Running all unit tests"
	@poetry run python -m pytest --cfx-version=26.1 $(PYTESTEXTRA) || poetry run python -m pytest --cfx-version=26.1 $(PYTESTRERUN)

unittest-all-261-no-codegen:
	@echo "Running all unit tests"
	@poetry run python -m pytest --cfx-version=26.1 -m "not codegen_required" $(PYTESTEXTRA) || poetry run python -m pytest --cfx-version=26.1 -m "not codegen_required" $(PYTESTRERUN)


api-codegen:
	@echo "Running API codegen"
	@python -m venv env
	@. env/bin/activate
	@pip install -q -e .
	@python codegen/allapigen.py
	@rm -rf env

build-doc-source:
	@sudo rm -rf doc/source/api/pre_processing
	@sudo rm -rf doc/source/api/post_processing
	@sudo rm -rf doc/source/api/solver
	@xvfb-run make -C doc html
