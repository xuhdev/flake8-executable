# Contributing 

To start developing, first create a virtual environment. Inside the virtual environment, install all development
dependencies:

    pip install -U .[dev]

To run lint:

    pre-commit run --all-files

To run runtime tests:

    pytest 
