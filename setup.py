#!/usr/bin/env python
"""
Python setup script for the Yagot project.
"""

import sys
import os
import re
import setuptools


def get_version(version_file):
    """
    Execute the specified version file and return the value of the __version__
    global variable that is set in the version file.

    Note: Make sure the version file does not depend on any packages in the
    requirements list of this package (otherwise it cannot be executed in
    a fresh Python environment).
    """
    with open(version_file, 'r') as fp:
        version_source = fp.read()
    _globals = {}
    exec(version_source, _globals)  # pylint: disable=exec-used
    return _globals['__version__']


def get_requirements(requirements_file):
    """
    Parse the specified requirements file and return a list of its non-empty,
    non-comment lines. The returned lines are without any trailing newline
    characters.
    """
    with open(requirements_file, 'r') as fp:
        lines = fp.readlines()
    reqs = []
    for line in lines:
        line = line.strip('\n')
        if not line.startswith('#') and line != '':
            reqs.append(line)
    return reqs


def read_file(a_file):
    """
    Read the specified file and return its content as one string.
    """
    with open(a_file, 'r') as fp:
        content = fp.read()
    return content


# pylint: disable=invalid-name
requirements = get_requirements('requirements.txt')
install_requires = [req for req in requirements
                    if req and not re.match(r'[^:]+://', req)]
dependency_links = [req for req in requirements
                    if req and re.match(r'[^:]+://', req)]
package_version = get_version(os.path.join('yagot', '_version.py'))

if 'develop' in sys.argv:
    ext_modules = [setuptools.Extension('test_leaky', ['tests/test_leaky.c'])]
else:
    ext_modules = []

# Docs on setup():
# * https://docs.python.org/2.7/distutils/apiref.html?
#   highlight=setup#distutils.core.setup
# * https://setuptools.readthedocs.io/en/latest/setuptools.html#
#   new-and-changed-setup-keywords
setuptools.setup(
    name='yagot',
    version=package_version,
    packages=[
        'yagot',
        'yagot_pytest',
    ],
    include_package_data=True,  # as specified in MANIFEST.in
    scripts=[
        # add any scripts
    ],
    entry_points={
        'pytest11': [
            'yagot = yagot_pytest.plugin',
        ],
    },
    ext_modules=ext_modules,
    install_requires=install_requires,
    dependency_links=dependency_links,

    description="Yet Another Garbage Object Tracker for Python",
    long_description=read_file('README.rst'),
    long_description_content_type='text/x-rst',
    license="Apache Software License 2.0",
    author="Andreas Maier",
    author_email='andreas.r.maier@gmx.de',
    maintainer="Andreas Maier",
    maintainer_email='andreas.r.maier@gmx.de',
    url='https://github.com/andy-maier/python-yagot',
    project_urls={
        'Bug Tracker': 'https://github.com/andy-maier/python-yagot/issues',
        'Documentation': 'https://yagot.readthedocs.io/en/latest/',
        'Source Code': 'https://github.com/andy-maier/python-yagot',
    },

    options={'bdist_wheel': {'universal': True}},
    zip_safe=True,  # This package can safely be installed from a zip file
    platforms='any',

    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
