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

from pathlib import Path
import unittest

from parameterized import parameterized

from flake8_executable import ExecutableChecker, exe001, exe002, exe003


class Flake8ExecutableTestCase(unittest.TestCase):

    _python_files_folder = 'to-be-tested/'

    @parameterized.expand([
        (exe001, 'exe001', {}),
        (exe002, 'exe002', {}),
        (exe003, 'exe003', {'shebang': '#!/bin/bash'})])
    def test_exe_positive(self, error, error_code, params):
        "Test EXE001, EXE002 and EXE003 cases in which an error should be reported."
        filename = Path(__file__).absolute().parent / (__class__._python_files_folder + error_code + '_pos.py')
        ec = ExecutableChecker(filename=str(filename))
        errors = tuple(ec.run())
        self.assertEqual(errors, (error(**params),))

    @parameterized.expand([
        'exe001',
        'exe002',
        'exe003'])
    def test_exe_negative(self, error_code):
        "Test EXE001, EXE002 and EXE003 cases in which no error should be reported."
        filename = Path(__file__).absolute().parent / (__class__._python_files_folder + error_code + '_neg.py')
        ec = ExecutableChecker(filename=str(filename))
        errors = tuple(ec.run())
        self.assertFalse(errors)  # errors should be empty


if __name__ == "__main__":
    unittest.main()
