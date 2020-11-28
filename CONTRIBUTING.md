To start developing, first create a virtual environment. Inside the virtual environment, install all development
dependencies:

    pip install -U -r requirements-dev.txt

Alternatively, install `tox` first. Then, let tox create the virtual environment for you:

    pip install -U --user tox
    tox -e dev
    . .tox/dev/bin/activate  # activate the virtual environment

To run lint:

    tox -e lint

To run runtime tests:

    tox --skip-missing-interpreters
