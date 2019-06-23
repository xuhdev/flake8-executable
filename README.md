# flake8-executable

Very often, developers mess up the executable permission of Python files: Sometimes the executable
permission was accidentally granted, sometimes it is forgotten.

This is a [Flake8][] plugin that ensures the executable permission of Python files is correctly
granted. Specifically, it checks the following two errors:

- EXE001: Shebang is present but the file is not executable.
- EXE002: The file is executable but no shebang is present.

## Installation

Simply run:

    pip install flake8-executable

## Usage

Normally, after flake8-executable is installed, invoking flake8 will also run this plugin. For more
details, check out the [Flake8 plugin page][].


[Flake8]: https://flake8.pycqa.org/
[Flake8 plugin page]: https://flake8.pycqa.org/en/latest/user/using-plugins.html
