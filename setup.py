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

```python
import platform
import os
import subprocess
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext as _build_ext


class BuildExt(_build_ext):
    def run(self):
        if platform.system() == "Windows":
            self.generate_import_lib()
        super().run()

    @staticmethod
    def generate_import_lib():
        dll_name = 'libhunspell-1.7-0.dll'
        def_name = 'libhunspell.def'
        lib_name = 'libhunspell-1.7-0.lib'
        hunspell_dir = os.path.join(os.path.dirname(__file__), 'bundled', 'windows', 'hunspell')
        dll_path = os.path.join(hunspell_dir, 'lib', dll_name)
        def_path = os.path.join(hunspell_dir, 'lib', def_name)
        lib_path = os.path.join(hunspell_dir, 'lib', lib_name)

        # Step 1: Generate the .def file
        dumpbin_command = f'dumpbin /EXPORTS {dll_path} > {def_path}'
        print(f'Running: {dumpbin_command}')
        subprocess.check_call(dumpbin_command, shell=True)

        # Step 2: Fix the .def file format
        with open(def_path, 'r') as f:
            lines = f.readlines()

        with open(def_path, 'w') as f:
            f.write(f'LIBRARY {dll_name}\n')
            f.write('EXPORTS\n')
            for line in lines:
                if 'ordinal' in line or 'hint' in line:
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    f.write(f'{parts[3]}\n')

        # Step 3: Generate the .lib file
        lib_command = f'lib /def:{def_path} /out:{lib_path} /machine:x64'
        print(f'Running: {lib_command}')
        subprocess.check_call(lib_command, shell=True)


def get_linux_include_dirs():
    return ['{}/hunspell'.format(d) for d in os.getenv('INCLUDE_PATH', '').split(':') if d]


main_module_kwargs = {"sources": ['hunspell.cpp'],
                      "language": "c++"}

if platform.system() == "Windows":
    path_prefix = os.path.dirname(__file__)
    hunspell_dir = os.path.join(path_prefix, 'bundled', 'windows', 'hunspell')
    main_module_kwargs['define_macros'] = [('HUNSPELL_STATIC', None)]
    main_module_kwargs['libraries'] = ['libhunspell-1.7-0']
    main_module_kwargs['include_dirs'] = [os.path.join(hunspell_dir, 'include', 'hunspell')]
    main_module_kwargs['library_dirs'] = [os.path.join(hunspell_dir, 'lib')]
    main_module_kwargs['extra_compile_args'] = ['/MD']
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
      long_description_content_type="text/markdown",  # so PyPI renders it properly
      author="Benoît Latinier",
      author_email="benoit@latinier.fr",
      url="http://github.com/blatinier/pyhunspell",
      ext_modules=[main],
      license="LGPLv3",
      cmdclass={'build_ext': BuildExt})
