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
import sys

import pytest

from flake8_executable import ExecutableChecker, EXE001, EXE002, EXE003, EXE004, EXE005

WIN32 = sys.platform.startswith("win")


class TestFlake8Executable:

    _python_files_folder = Path(__file__).absolute().parent / 'to-be-tested'

    @classmethod
    def _get_pos_filename(cls, error_code):
        "Get the filename for which an error of error_code should be emitted (on POSIX, Windows might be different)."
        return cls._python_files_folder / (error_code + '_pos.py')

    @classmethod
    def _get_neg_filename(cls, error_code):
        """Get the filename for which an error of error_code should not be emitted (on POSIX, Windows might be
        different)."""
        return cls._python_files_folder / (error_code + '_neg.py')

    @pytest.mark.parametrize("error, error_code", [
        pytest.param(EXE001(line_number=1), 'exe001',
                     marks=pytest.mark.skipif(WIN32, reason="Windows doesn't support EXE001")),
        pytest.param(EXE002(), 'exe002', marks=pytest.mark.skipif(WIN32, reason="Windows doesn't support EXE002")),
        (EXE003(line_number=1, shebang='#!/bin/bash'), 'exe003'),
        (EXE004(line_number=1, offset=4), 'exe004'),
        (EXE005(line_number=3), 'exe005')])
    def test_exe_positive(self, error, error_code):
        "Test cases in which an error should be reported."
        filename = __class__._get_pos_filename(error_code)
        ec = ExecutableChecker(filename=str(filename))
        errors = tuple(ec.run())
        assert errors == (error(),)

    @pytest.mark.skipif(not WIN32, reason="Windows-only test.")
    @pytest.mark.parametrize("error_code", [
        'exe001',
        'exe002'])
    def test_exe_positive_others_but_negative_windows(self, error_code):
        "Test cases in which an error should not be reported on Windows, while they are reported on Linux."
        filename = __class__._get_pos_filename(error_code)
        ec = ExecutableChecker(filename=str(filename))
        errors = tuple(ec.run())
        assert not errors  # errors should be empty

    @pytest.mark.parametrize("error_code", [
        'exe001',
        'exe002',
        'exe003',
        'exe004',
        'exe005'])
    def test_exe_negative(self, error_code):
        "Test cases in which no error should be reported."
        filename = __class__._get_neg_filename(error_code)
        ec = ExecutableChecker(filename=str(filename))
        errors = tuple(ec.run())
        assert not errors  # errors should be empty

    @staticmethod
    def _run_checker_stdin_from_file(filename):
        with open(filename) as f:
            lines = f.readlines()
        ec = ExecutableChecker(filename='-', lines=lines)
        return tuple(ec.run())

    @pytest.mark.parametrize("error, error_code", [
        (EXE003(line_number=1, shebang='#!/bin/bash'), 'exe003'),
        (EXE004(line_number=1, offset=4), 'exe004'),
        (EXE005(line_number=3), 'exe005')])
    def test_stdin_positive(self, error, error_code):
        "Test case in which an error should be reported (input is stdin)."
        filename = __class__._get_pos_filename(error_code)
        errors = __class__._run_checker_stdin_from_file(filename)
        assert errors == (error(),)

    @pytest.mark.parametrize("error_code", [
        'exe001',
        'exe002',
        'exe003',
        'exe004',
        'exe005'])
    def test_stdin_negative(self, error_code):
        "Test cases in which no error should be reported (input is stdin)."
        filename = __class__._get_neg_filename(error_code)
        errors = __class__._run_checker_stdin_from_file(filename)
        assert not errors  # errors should be empty

    @pytest.mark.parametrize("error_code", [
        'exe001',
        'exe002'])
    def test_stdin_negative_otherwise_positive(self, error_code):
        "Test errors that should not be emitted when the input is from stdin, even if they should be otherwise emitted."
        filename = __class__._get_pos_filename(error_code)
        errors = __class__._run_checker_stdin_from_file(filename)
        assert not errors  # errors should be empty

    @pytest.mark.parametrize("filename", ['-', 'stdin'])
    def test_stdin_negative_empty(self, filename):
        "Test empty input from stdin."
        ec = ExecutableChecker(filename=filename, lines=[])
        assert len(tuple(ec.run())) == 0

    def test_cli(self):
        "Test the flake8 CLI interface and ensure there's no crash."
        import flake8.main.application

        # The following line must not raise any exception
        flake8.main.application.Application().run([str(self._python_files_folder)])


if __name__ == "__main__":
    pytest.main([__file__])
