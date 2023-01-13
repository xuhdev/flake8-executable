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
import os
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable, List, Optional, Tuple, Union

from ._version import __version__

SHEBANG_REGEX = re.compile(r"(\s*)#!")


class Error(ABC):
    """Base class of all errors.

    :param line_number: Line number of the error.
    :param offset: Offset of the error.
    :param error_code: Error code of the error.
    :param message: Message of the error.
    :param kwargs: Ignored. This is for the convenience of inheriting and calling super().__init__().
    """

    @abstractmethod
    def __init__(
        self,
        line_number: int,
        offset: int,
        error_code: str,
        message: str,
        **kwargs: Any,
    ) -> None:
        self.line_number = line_number
        self.offset = offset
        self.error_code = error_code
        self.message = message

    @staticmethod
    def format_flake8(
        line_number: int, offset: int, error_code: str, message: str
    ) -> Tuple[int, int, str, str]:
        """Return a format of that Flake8 accepts."""
        return line_number, offset, f"{error_code} {message}", ""

    def __call__(self) -> Tuple[int, int, str, str]:
        return self.__class__.format_flake8(
            self.line_number, self.offset, self.error_code, self.message
        )

    @classmethod
    def should_check(cls, *args: Any, **kwargs: Any) -> bool:
        """Whether this error should be checked. The base class currently will always return True but this can change,
        so you should always check the return value of this function when overriding."""
        return True


class UnixError(Error, ABC):
    @classmethod
    def should_check(cls, filename: Union[os.PathLike, str], **kwargs: Any) -> bool:
        # Do not check on Windows or the input is not a file in the filesystem.
        return (
            os.name != "nt"
            and filename is not None
            and str(filename) not in ("-", "stdin")
            and super().should_check(filename=filename, **kwargs)
        )


class EXE001(UnixError):
    def __init__(self, line_number: int, **kwargs: Any) -> None:
        super().__init__(
            line_number,
            0,
            "EXE001",
            "Shebang is present but the file is not executable.",
            **kwargs,
        )


class EXE002(UnixError):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(
            0,
            0,
            "EXE002",
            "The file is executable but no shebang is present.",
            **kwargs,
        )


class EXE003(Error):
    def __init__(self, line_number: int, shebang: str, **kwargs: Any) -> None:
        super().__init__(
            line_number,
            0,
            "EXE003",
            'Shebang is present but does not contain "python": ' + shebang,
            **kwargs,
        )


class EXE004(Error):
    def __init__(self, line_number: int, offset: int, **kwargs: Any):
        super().__init__(
            line_number,
            offset,
            "EXE004",
            "There is whitespace before shebang.",
            **kwargs,
        )


class EXE005(Error):
    def __init__(self, line_number: int, **kwargs: Any):
        super().__init__(
            line_number,
            0,
            "EXE005",
            "There are blank or comment lines before shebang.",
            **kwargs,
        )


class EXE006(Error):
    def __init__(self, **kwargs: Any):
        super().__init__(
            0,
            0,
            "EXE006",
            "Found shebang, but no __name__ == '__main__'.",
            **kwargs,
        )


class EXE007(UnixError):
    def __init__(self, **kwargs: Any):
        super().__init__(
            0,
            0,
            "EXE007",
            "The file is executable, but no __name__ == '__main__'.",
            **kwargs,
        )


class MainAnalyzer(ast.NodeVisitor):
    """Detect __name__ == '__main__'"""

    has_main = False

    def visit_If(self, node: ast.If) -> None:
        if isinstance(node.test, ast.Compare):
            c = node.test
            if (
                (len(c.ops) == 1 and isinstance(c.ops[0], ast.Eq))
                and len(c.comparators) == 1
                and (
                    isinstance(c.left, ast.Name)
                    and c.left.id == "__name__"
                    and (
                        isinstance(c.comparators[0], ast.Constant)
                        and c.comparators[0].value == "__main__"
                    )
                    or
                    # py <= 3.7
                    (
                        isinstance(c.comparators[0], ast.Str)
                        and c.comparators[0].s == "__main__"
                    )
                )
                or (
                    (isinstance(c.left, ast.Str) and c.left.s == "__main__")
                    or (isinstance(c.left, ast.Constant) and c.left.value == "__main__")
                    and isinstance(c.comparators[0], ast.Name)
                    and c.comparators[0].id == "__name__"
                )
            ):
                self.has_main = True
            else:
                print(ast.dump(c))
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Prevent functions from being evaluated"""
        # self.generic_visit(node)
        return node


class ExecutableChecker:
    name = "flake8-executable"
    version = __version__

    def __init__(
        self,
        tree: ast.AST,
        filename: Union[os.PathLike, str] = "",
        lines: Optional[List[str]] = None,
    ) -> None:
        self.tree = tree
        self.filename = Path(filename)

        # Get lines if it is not already read
        if lines is None:
            self.lines = self.filename.read_text().splitlines()
        else:
            self.lines = lines

    def _check_main(self) -> bool:
        ma = MainAnalyzer()
        ma.visit(self.tree)
        return ma.has_main or self.filename.name == "__main__.py"

    def _check_shebang(self) -> Optional[Tuple[int, str, int]]:
        shebang = None
        for i, line in enumerate(self.lines, 1):
            m = SHEBANG_REGEX.match(line)
            if m:
                # shebang found
                shebang = (i, line, len(m.group(1)))
                break

            line = line.strip()
            if len(line) != 0 and not line.startswith("#"):
                # neither blank nor comment line
                break
        return shebang

    def _check_executable(self) -> bool:
        return os.access(self.filename, os.X_OK)

    def get_flake8_codes(
        self, main: bool, shebang: Optional[Tuple[int, str, int]], is_executable: bool
    ) -> Iterable[Tuple[int, int, str, str]]:
        if shebang is not None:
            if shebang[2] > 0 and EXE004.should_check():
                yield EXE004(line_number=shebang[0], offset=shebang[2])()

            if not is_executable and EXE001.should_check(
                filename=self.filename
            ):  # pragma: no cover windows. No execution of this branch on Windows
                yield EXE001(line_number=shebang[0])()
            if "python" not in shebang[1] and EXE003.should_check():
                yield EXE003(line_number=shebang[0], shebang=shebang[1].strip())()
            if shebang[0] > 1 and EXE005.should_check():
                yield EXE005(line_number=shebang[0])()
            if not main and EXE006.should_check(filename=self.filename):
                yield EXE006()()
        elif (
            is_executable
        ):  # pragma: no cover windows. No execution of this branch on Windows
            # In principle, this error may also be yielded on empty
            # files, but flake8 seems to always skip empty files.
            if EXE002.should_check(filename=self.filename):
                yield EXE002()()
            if not main and EXE007.should_check(filename=self.filename):
                yield EXE007()()

    def run(self) -> Optional[Iterable[Error]]:
        main = self._check_main()
        shebang = self._check_shebang()
        is_executable = self._check_executable()

        yield from self.get_flake8_codes(main, shebang, is_executable)


__all__ = (
    "__version__",
    "ExecutableChecker",
    "Error",
    "EXE001",
    "EXE002",
    "EXE003",
    "EXE004",
    "EXE005",
    "EXE006",
    "EXE007",
)
