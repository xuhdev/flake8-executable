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

from collections import namedtuple
import os

from .version import __version__

Error = namedtuple('Error', ['line_number', 'offset', 'message', 'check'])

EXE001 = Error(0, 0, ('EXE001' ' Shebang is present but the file is not executable.'), '')
EXE002 = Error(0, 0, ('EXE002' ' The file is executable but no shebang is present.'), '')


class ExecutableChecker:
    name = 'flake8-executable'
    version = __version__

    def __init__(self, tree=None, filename=None, lines=None):
        self.filename = filename
        self.lines = lines

    def run(self):
        if (os.name == 'nt' or  # Executable checks on Windows make no sense
                self.filename is None):  # A concrete physical file is needed for testing
            return

        # Get first line
        if self.lines:
            first_line = self.lines[0]
        else:
            with open(self.filename) as f:
                first_line = f.readline()

        has_shebang = first_line.startswith('#!')
        is_executable = os.access(self.filename, os.X_OK)
        if has_shebang and not is_executable:
            yield EXE001
        elif not has_shebang and is_executable:
            # In principle, this error may also be yielded on empty
            # files, but flake8 seems to always skip empty files.
            yield EXE002
