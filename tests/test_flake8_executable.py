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

from flake8_executable import ExecutableChecker, EXE001, EXE002


class Flake8ExecutableTestCase(unittest.TestCase):

    _python_files_folder = 'to-be-tested/'

    @parameterized.expand([
        (EXE001, 'exe001'),
        (EXE002, 'exe002')])
    def test_exe_positive(self, error, error_code):
        "Test cases in which an error should be reported."
        filename = Path(__file__).absolute().parent / (self._python_files_folder + error_code + '_pos.py')
        ec = ExecutableChecker(filename=str(filename))
        errors = tuple(ec.run())
        self.assertEqual(errors, (error,))

    @parameterized.expand([
        'exe001',
        'exe002'])
    def test_exe_negative(self, error_code):
        "Test cases in which no error should be reported."
        filename = Path(__file__).absolute().parent / (self._python_files_folder + error_code + '_neg.py')
        ec = ExecutableChecker(filename=str(filename))
        errors = tuple(ec.run())
        self.assertFalse(errors)


if __name__ == "__main__":
    unittest.main()
