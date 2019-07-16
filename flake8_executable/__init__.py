# Copyright (c) 2019 Hong Xu <hong@topbug.net>

# This file is part of flake8-executable.

# flake8-executable is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# flake8-executable is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License
# for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with flake8-executable. If not, see <https://www.gnu.org/licenses/>.

from abc import ABC
import os
import re

from .version import __version__


class Error(ABC):
    "Base class of all errors."

    def __init__(self, line_number, offset, error_code, message, check, **kwargs):
        self.line_number = line_number
        self.offset = offset
        self.error_code = error_code
        self.message = message
        self.check = check

    @staticmethod
    def format_flake8(line_number, error_code, offset, message, check):
        "Return a format of that Flake8 accepts."
        return line_number, offset, '{} {}'.format(error_code, message), check

    def __call__(self):
        return __class__.format_flake8(self.line_number, self.error_code, self.offset, self.message, self.check)

    @classmethod
    def should_check(cls, **kwargs) -> bool:
        "Whether this error should be checked."
        return True


class EXE001(Error):
    def __init__(self, line_number, **kwargs):
        super().__init__(line_number, 0, 'EXE001', 'Shebang is present but the file is not executable.', '')

    @classmethod
    def should_check(cls, filename, **kwargs) -> bool:  # noqa: T484
        # Do not check on Windows or the input is not a file in the filesystem.
        return os.name != 'nt' and filename is not None and filename not in ('-', 'stdin')


class EXE002(Error):
    def __init__(self, **kwargs):
        super().__init__(0, 0, 'EXE002', 'The file is executable but no shebang is present.', '')

    @classmethod
    def should_check(cls, filename, **kwargs) -> bool:  # noqa: T484
        # Do not check on Windows or the input is not a file in the filesystem.
        return os.name != 'nt' and filename is not None and filename not in ('-', 'stdin')


class EXE003(Error):
    def __init__(self, line_number, shebang, **kwargs):
        super().__init__(line_number, 0, 'EXE003', 'Shebang is present but does not contain "python": ' + shebang, '')


class EXE004(Error):
    def __init__(self, line_number, offset, **kwargs):
        super().__init__(line_number, offset, 'EXE004', 'There is whitespace before shebang.', '')


class EXE005(Error):
    def __init__(self, line_number, **kwargs):
        super().__init__(line_number, 0, 'EXE005', 'There are blank or comment lines before shebang.', '')


class ExecutableChecker:
    name = 'flake8-executable'
    version = __version__

    def __init__(self, tree=None, filename=None, lines=None):
        self.filename = filename
        self.lines = lines

    def run(self):
        # Get lines if its not already read
        if self.lines is None:
            with open(self.filename) as f:
                self.lines = f.readlines()

        shebang_lineno = None
        for i, line in enumerate(self.lines, 1):
            m = re.match(r'(\s*)#!', line)
            if m:  # shebang found
                shebang_lineno = i
                shebang_line = line
                if m.group(1):
                    if EXE004.should_check():
                        yield EXE004(line_number=shebang_lineno, offset=len(m.group(1)))()
                break

            line = line.strip()
            if len(line) != 0 and not line.startswith('#'):  # neither blank or comment line
                break

        is_executable = os.access(self.filename, os.X_OK)
        if shebang_lineno is not None:
            if not is_executable:
                if EXE001.should_check(filename=self.filename):
                    yield EXE001(line_number=shebang_lineno)()
            if 'python' not in shebang_line:
                if EXE003.should_check():
                    yield EXE003(line_number=shebang_lineno, shebang=shebang_line.strip())()
            if shebang_lineno > 1:
                if EXE005.should_check():
                    yield EXE005(line_number=shebang_lineno)()
        elif is_executable:
            # In principle, this error may also be yielded on empty
            # files, but flake8 seems to always skip empty files.
            if EXE002.should_check(filename=self.filename):
                yield EXE002()()
