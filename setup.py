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

import pathlib

from setuptools import setup


setup(
    name="flake8-executable",
    description="A Flake8 plugin for checking executable permissions and shebangs.",
    long_description=pathlib.Path('README.md').read_text(),
    long_description_content_type="text/markdown",
    keywords="flake8 linter qa",
    author="Hong Xu",
    author_email="hong@topbug.net",
    url="https://github.com/xuhdev/flake8-executable",
    license='LGPL v3+',
    packages=["flake8_executable"],
    data_files=[("", ["COPYING", "COPYING.GPL"])],
    python_requires=">=3.6",
    install_requires=["flake8 >= 3.0.0"],
    classifiers=[
        "Environment :: Console",
        "Framework :: Flake8",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
    ],
    entry_points={
        "flake8.extension": ["EXE00 = flake8_executable:ExecutableChecker"]
    },
    use_scm_version={'write_to': 'flake8_executable/_version.py'},
    setup_requires=['setuptools_scm']
)
