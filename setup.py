#!/usr/bin/env python3
"""
Run 'python3 setup.py install' to install Unicycler.
"""

import sys
import os
import shutil
from distutils.command.build import build
from distutils.core import Command
import subprocess
import multiprocessing
import fnmatch
import importlib.util

# Make sure this is being run with Python 3.4 or later.
if sys.version_info.major != 3 or sys.version_info.minor < 4:
    print('Error: you must execute setup.py using Python 3.4 or later')
    sys.exit(1)

# Install setuptools if not already present.
if not importlib.util.find_spec("setuptools"):
    # noinspection PyPackageRequirements
    import ez_setup
    ez_setup.use_setuptools()

# noinspection PyPep8
from setuptools import setup
# noinspection PyPep8
from setuptools.command.install import install

# Get the program version from another file.
exec(open('unicycler/version.py').read())

with open('README.md', 'rb') as readme:
    LONG_DESCRIPTION = readme.read().decode('utf-8')


class UnicycleBuild(build):
    """
    The build process runs the Makefile to build the C++ functions into a shared library.
    """

    def run(self):
        build.run(self)  # Run original build code
        try:
            cmd = ['make', '-j', str(max(8, multiprocessing.cpu_count()))]
        except NotImplementedError:
            cmd = ['make']

        def compile_cpp():
            subprocess.call(cmd)

        self.execute(compile_cpp, [], 'Compiling Unicycler: ' + ' '.join(cmd))


class UnicycleInstall(install):
    """
    The install process copies the C++ shared library to the install location.
    """

    def run(self):
        install.run(self)  # Run original install code
        shutil.copyfile('unicycler/cpp_functions.so',
                        os.path.join(self.install_lib, 'unicycler', 'cpp_functions.so'))


class UnicycleClean(Command):
    """
    Custom clean command that really cleans up everything, except for:
      - the compiled *.so file needed when running the programs
      - setuptools-*.egg file needed when running this script
    """
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd

        delete_directories = []
        for root, dir_names, filenames in os.walk(self.cwd):
            for dir_name in fnmatch.filter(dir_names, '*.egg-info'):
                delete_directories.append(os.path.join(root, dir_name))
            for dir_name in fnmatch.filter(dir_names, 'build'):
                delete_directories.append(os.path.join(root, dir_name))
            for dir_name in fnmatch.filter(dir_names, '__pycache__'):
                delete_directories.append(os.path.join(root, dir_name))
        for delete_directory in delete_directories:
            print('Deleting directory:', delete_directory)
            shutil.rmtree(delete_directory)

        delete_files = []
        for root, dir_names, filenames in os.walk(self.cwd):
            for filename in fnmatch.filter(filenames, 'setuptools*.zip'):
                delete_files.append(os.path.join(root, filename))
            for filename in fnmatch.filter(filenames, '*.o'):
                delete_files.append(os.path.join(root, filename))
            for filename in fnmatch.filter(filenames, '*.pyc'):
                delete_files.append(os.path.join(root, filename))
        for delete_file in delete_files:
            print('Deleting file:', delete_file)
            os.remove(delete_file)


setup(name='unicycler',
      version=__version__,
      description='bacterial genome assembler for hybrid read sets',
      long_description=LONG_DESCRIPTION,
      url='http://github.com/rrwick/unicycler',
      author='Ryan Wick',
      author_email='rrwick@gmail.com',
      license='GPL',
      packages=['unicycler'],
      entry_points={"console_scripts": ['unicycler = unicycler.unicycler:main',
                                        'antpath = unicycler.antpath:main',
                                        'scrutinate = unicycler.scrutinate:main']},
      zip_safe=False,
      cmdclass={'build': UnicycleBuild,
                'install': UnicycleInstall,
                'clean': UnicycleClean}
      )
