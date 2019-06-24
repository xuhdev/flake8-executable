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

from flake8_executable import ExecutableChecker, EXE001, EXE002, EXE003


class Flake8ExecutableTestCase(unittest.TestCase):

    _python_files_folder = Path(__file__).absolute().parent / 'to-be-tested'

    @classmethod
    def _get_pos_filename(cls, error_code):
        "Get the filename for which an error of error_code should be emitted."
        return cls._python_files_folder / (error_code + '_pos.py')

    @classmethod
    def _get_neg_filename(cls, error_code):
        "Get the filename for which an error of error_code should not be emitted."
        return cls._python_files_folder / (error_code + '_neg.py')

    @parameterized.expand([
        (EXE001(), 'exe001'),
        (EXE002(), 'exe002'),
        (EXE003(shebang='#!/bin/bash'), 'exe003')])
    def test_exe_positive(self, error, error_code):
        "Test cases in which an error should be reported."
        filename = __class__._get_pos_filename(error_code)
        ec = ExecutableChecker(filename=str(filename))
        errors = tuple(ec.run())
        self.assertEqual(errors, (error(),))

    @parameterized.expand([
        'exe001',
        'exe002',
        'exe003'])
    def test_exe_negative(self, error_code):
        "Test cases in which no error should be reported."
        filename = __class__._get_neg_filename(error_code)
        ec = ExecutableChecker(filename=str(filename))
        errors = tuple(ec.run())
        self.assertFalse(errors)  # errors should be empty

    @staticmethod
    def _run_checker_stdin_from_file(filename):
        with open(filename) as f:
            lines = f.readlines()
        ec = ExecutableChecker(filename='-', lines=lines)
        return tuple(ec.run())

    @parameterized.expand([
        (EXE003(shebang='#!/bin/bash'), 'exe003')])
    def test_stdin_positive(self, error, error_code):
        "Test case in which an error should be reported (input is stdin)."
        filename = __class__._get_pos_filename(error_code)
        errors = __class__._run_checker_stdin_from_file(filename)
        self.assertEqual(errors, (error(),))

    @parameterized.expand([
        'exe001',
        'exe002',
        'exe003'])
    def test_stdin_negative(self, error_code):
        "Test cases in which no error should be reported (input is stdin)."
        filename = __class__._get_neg_filename(error_code)
        errors = __class__._run_checker_stdin_from_file(filename)
        self.assertFalse(errors)  # errors should be empty

    @parameterized.expand([
        'exe001',
        'exe002'])
    def test_stdin_negative_otherwise_positive(self, error_code):
        "Test errors that should not be emitted when the input is from stdin, even if they should be otherwise emitted."
        filename = __class__._get_pos_filename(error_code)
        errors = __class__._run_checker_stdin_from_file(filename)
        self.assertFalse(errors)  # errors should be empty


if __name__ == "__main__":
    unittest.main()
