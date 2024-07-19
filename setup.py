#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
This file is part of PyHunspell.

PyHunspell is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyHunspell is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyHunspell. If not, see <http://www.gnu.org/licenses/>.
"""

import os
import platform
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext


# Helper function to find MinGW path
def find_mingw():
    possible_paths = [
        "C:\\MinGW\\bin",
        "C:\\mingw64\\bin",
        "C:\\Program Files\\mingw-w64\\x86_64-8.1.0-win32-seh-rt_v6-rev0\\mingw64\\bin",
        # Add more paths if needed
    ]
    for path in possible_paths:
        if os.path.isdir(path):
            return path
    return None


class build_ext_mingw(_build_ext):
    def build_extensions(self):
        # Set the MinGW compiler and linker
        os.environ['CC'] = 'gcc'
        os.environ['CXX'] = 'g++'
        if platform.system() == "Windows":
            mingw_path = find_mingw()
            if not mingw_path:
                raise RuntimeError("MinGW path not found. Please install MinGW and add it to your PATH.")

            for ext in self.extensions:
                ext.extra_compile_args = ['-static-libgcc', '-static-libstdc++']
                ext.extra_link_args = ['-static-libgcc', '-static-libstdc++']

        super().build_extensions()


def get_linux_include_dirs():
    return ['{}/hunspell'.format(d) for d in os.getenv('INCLUDE_PATH', '').split(':') if d]


main_module_kwargs = {"sources": ['hunspell.cpp'],
                      "language": "c++"}

if platform.system() == "Windows":
    path_prefix = os.path.dirname(__file__)
    bundled_dir = os.path.join(path_prefix, 'bundled', 'windows')
    hunspell_dir = os.path.join(bundled_dir, 'hunspell')
    main_module_kwargs['define_macros'] = [('HUNSPELL_STATIC', None)]
    main_module_kwargs['libraries'] = ['hunspell-1.7-0']
    main_module_kwargs['include_dirs'] = [os.path.join(hunspell_dir, 'include', 'hunspell')]
    main_module_kwargs['library_dirs'] = [os.path.join(hunspell_dir, 'lib')]
    main_module_kwargs['extra_compile_args'] = ['-static-libgcc', '-static-libstdc++']
    main_module_kwargs['extra_link_args'] = ['-static-libgcc', '-static-libstdc++']
    print(f"Include dirs: {main_module_kwargs['include_dirs']}")
elif platform.system() == "Darwin":
    main_module_kwargs['define_macros'] = [('_LINUX', None)]
    main_module_kwargs['libraries'] = ['hunspell']
    main_module_kwargs['include_dirs'] = ['/usr/local/include/hunspell']
    main_module_kwargs['extra_compile_args'] = ['-Wall']
else:
    main_module_kwargs['define_macros'] = [('_LINUX', None)]
    main_module_kwargs['libraries'] = ['hunspell']
    main_module_kwargs['include_dirs'] = get_linux_include_dirs() + ['/usr/include/hunspell']
    main_module_kwargs['extra_compile_args'] = ['-Wall']

main = Extension('hunspell', **main_module_kwargs)

setup(name="hunspell",
      version="0.5.5",
      description="Module for the Hunspell spellchecker engine",
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      author="Benoît Latinier",
      author_email="benoit@latinier.fr",
      url="http://github.com/blatinier/pyhunspell",
      ext_modules=[main],
      license="LGPLv3",
      cmdclass={'build_ext': build_ext_mingw})
