# flake8-executable

[![Pyversions](https://img.shields.io/pypi/pyversions/flake8-executable.svg?style=flat-square)](https://pypi.python.org/pypi/flake8-executable)
![PyPI](https://img.shields.io/pypi/v/flake8-executable.svg)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flake8-executable)
[![Build Status](https://ci.appveyor.com/api/projects/status/h6mucl894w6dx7d0?svg=true)](https://ci.appveyor.com/project/xuhdev/flake8-executable)

Very often, developers mess up the executable permissions and shebangs of Python files. For example,
sometimes the executable permission was accidentally granted, sometimes it is forgotten.

This is a [Flake8][] plugin that ensures the executable permissions and shebangs of Python files are
correctly set. Specifically, it checks the following errors:

- EXE001: Shebang is present but the file is not executable.
- EXE002: The file is executable but no shebang is present.
- EXE003: Shebang is present but does not contain "python".
- EXE004: There is whitespace before shebang.
- EXE005: There are blank or comment lines before shebang.

## Installation

Run:

    pip install flake8-executable

## Usage

Normally, after flake8-executable is installed, invoking flake8 will also run this plugin. For more
details, check out the [Flake8 plugin page][].

## Copyright and License

Copyright (c) 2019 Hong Xu <hong@topbug.net>

flake8-executable is free software: you can redistribute it and/or modify it under the terms of the
GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

flake8-executable is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with
flake8-executable. If not, see <https://www.gnu.org/licenses/>.



[Flake8]: https://flake8.pycqa.org/
[Flake8 plugin page]: https://flake8.pycqa.org/en/latest/user/using-plugins.html
