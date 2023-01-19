# Copyright (c) 2019 Hong Xu <hong@topbug.net>
# Copyright (c) 2023 Simon Brugman

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


import ast
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import pytest

from flake8_executable import (
    EXE001,
    EXE002,
    EXE003,
    EXE004,
    EXE005,
    EXE006,
    EXE007,
    Error,
    ExecutableChecker,
)

WIN32 = sys.platform.startswith("win")


class TestFlake8Executable:
    _python_files_folder = Path(__file__).absolute().parent / "to-be-tested"

    def _get_filename(self, error_code: str) -> Path:
        """Get the filename for the test file (on POSIX, Windows might be different)."""
        return self._python_files_folder / (error_code + ".py")

    @pytest.mark.parametrize(
        "test_name,main,executable,shebang,errors",
        [
            ("empty", False, WIN32, None, []),
            ("__main__", True, WIN32, None, []),
            ("main_off", False, WIN32, None, []),
            pytest.param(
                "exe001_pos",
                True,
                False,
                (1, "#!/usr/bin/python", 0),
                [EXE001(line_number=1)()],
                marks=pytest.mark.skipif(
                    WIN32, reason="Windows doesn't support EXE001"
                ),
            ),
            pytest.param(
                "exe001_pos",
                True,
                True,
                (1, "#!/usr/bin/python", 0),
                [],
                marks=pytest.mark.skipif(
                    not WIN32, reason="Windows doesn't support EXE001"
                ),
            ),
            pytest.param(
                "shebang_only",
                False,
                False,
                (1, "#!/usr/bin/python", 0),
                [EXE001(line_number=1)(), EXE006()()],
                marks=pytest.mark.skipif(
                    WIN32, reason="Windows doesn't support EXE001"
                ),
            ),
            pytest.param(
                "shebang_only",
                False,
                True,
                (1, "#!/usr/bin/python", 0),
                [EXE006()()],
                marks=pytest.mark.skipif(
                    not WIN32, reason="Windows doesn't support EXE001"
                ),
            ),
            pytest.param(
                "exe002_pos",
                True,
                True,
                None,
                [EXE002()()],
                marks=pytest.mark.skipif(
                    WIN32, reason="Windows doesn't support EXE001"
                ),
            ),
            pytest.param(
                "exe002_pos",
                True,
                True,
                None,
                [],
                marks=pytest.mark.skipif(
                    not WIN32, reason="Windows doesn't support EXE001"
                ),
            ),
            (
                "exe003_pos",
                True,
                True,
                (1, "#!/bin/bash", 0),
                [EXE003(line_number=1, shebang="#!/bin/bash")()],
            ),
            (
                "exe004_pos",
                True,
                True,
                (1, "    #!/usr/bin/python3", 4),
                [EXE004(line_number=1, offset=4)()],
            ),
            (
                "exe005_pos",
                True,
                True,
                (3, "#!/usr/bin/python3", 0),
                [EXE005(line_number=3)()],
            ),
            ("exe006_pos", False, True, (1, "#!/usr/bin/python3", 0), [EXE006()()]),
            ("exe006_2_pos", False, True, (1, "#!/usr/bin/python3", 0), [EXE006()()]),
            pytest.param(
                "exe007_pos",
                False,
                True,
                None,
                [EXE002()(), EXE007()()],
                marks=pytest.mark.skipif(
                    WIN32, reason="Windows doesn't support EXE001"
                ),
            ),
            pytest.param(
                "exe007_pos",
                False,
                True,
                None,
                [],
                marks=pytest.mark.skipif(
                    not WIN32, reason="Windows doesn't support EXE001"
                ),
            ),
            ("exe001_neg", True, WIN32, None, []),
            ("exe002_neg", True, WIN32, None, []),
            ("exe003_neg", True, True, (1, "#!/usr/bin/python3", 0), []),
            ("exe004_neg", True, True, (1, "#!/usr/bin/python3", 0), []),
            ("exe005_neg", True, True, (1, "#!/usr/bin/python3", 0), []),
            ("exe006_neg", True, True, (1, "#!/usr/bin/python3", 0), []),
            ("exe006_2_neg", True, True, (1, "#!/usr/bin/python3", 0), []),
        ],
    )
    def test_checker(
        self,
        test_name: str,
        main: bool,
        executable: bool,
        shebang: Optional[Tuple[int, str, int]],
        errors: List[Error],
    ):
        file_name = self._get_filename(test_name)
        tree = ast.parse(file_name.read_text())

        ec = ExecutableChecker(tree=tree, filename=str(file_name))
        assert ec._check_main() == main
        assert ec._check_shebang() == shebang
        assert ec._check_executable() == executable

        codes = list(ec.get_flake8_codes(main, shebang, executable))
        assert codes == errors

    @pytest.mark.parametrize(
        "test_name,main,shebang,errors",
        [
            ("empty", False, None, []),
            ("__main__", False, None, []),
            ("main_off", False, None, []),
            ("exe001_pos", True, (1, "#!/usr/bin/python", 0), []),
            ("shebang_only", False, (1, "#!/usr/bin/python", 0), [EXE006()()]),
            ("exe002_pos", True, None, []),
            (
                "exe003_pos",
                True,
                (1, "#!/bin/bash", 0),
                [EXE003(line_number=1, shebang="#!/bin/bash")()],
            ),
            (
                "exe004_pos",
                True,
                (1, "    #!/usr/bin/python3", 4),
                [EXE004(line_number=1, offset=4)()],
            ),
            (
                "exe005_pos",
                True,
                (3, "#!/usr/bin/python3", 0),
                [EXE005(line_number=3)()],
            ),
            ("exe006_pos", False, (1, "#!/usr/bin/python3", 0), [EXE006()()]),
            ("exe006_2_pos", False, (1, "#!/usr/bin/python3", 0), [EXE006()()]),
            ("exe007_pos", False, None, []),
            ("exe001_neg", True, None, []),
            ("exe002_neg", True, None, []),
            ("exe003_neg", True, (1, "#!/usr/bin/python3", 0), []),
            ("exe004_neg", True, (1, "#!/usr/bin/python3", 0), []),
            ("exe005_neg", True, (1, "#!/usr/bin/python3", 0), []),
            ("exe006_neg", True, (1, "#!/usr/bin/python3", 0), []),
            ("exe006_2_neg", True, (1, "#!/usr/bin/python3", 0), []),
        ],
    )
    def test_stdin(self, test_name, main, shebang, errors):
        file_name = self._get_filename(test_name)
        text = file_name.read_text()
        lines = text.splitlines()
        tree = ast.parse(text)

        ec = ExecutableChecker(tree=tree, filename="-", lines=lines)
        assert ec._check_main() == main
        assert ec._check_shebang() == shebang

        codes = list(ec.get_flake8_codes(main, shebang, False))
        assert codes == errors

    def test_cli(self):
        """Test the flake8 CLI interface and ensure there's no crash."""
        import flake8.main.application

        # The following line must not raise any exception
        flake8.main.application.Application().run([str(self._python_files_folder)])


if __name__ == "__main__":
    pytest.main([__file__])
