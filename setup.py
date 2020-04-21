#!/usr/bin/env python

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import os.path as op

from setuptools import setup, find_packages

# get the version (don't import saber here, so dependencies are not needed)
version = None
with open(op.join('saber', '__init__.py'), 'r') as fid:
    for line in (line.strip() for line in fid):
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('\'')
            break
if version is None:
    raise RuntimeError('Could not determine version')


descr = """SABER: Search A/B Experiment Report."""

DISTNAME = 'saber'
DESCRIPTION = descr
AUTHOR = 'Ben Miroglio'
AUTHOR_EMAIL = 'bmiroglio@mozilla.com'
MAINTAINER = 'Teon L Brooks'
MAINTAINER_EMAIL = 'teon@mozilla.com'
LICENSE = 'MPL 2.0'
DOWNLOAD_URL = 'http://github.com/bmiroglio/saber'
VERSION = version


if __name__ == "__main__":

    setup(name=DISTNAME,
          author=AUTHOR,
          author_email=AUTHOR_EMAIL,
          maintainer=MAINTAINER,
          include_package_data=True,
          maintainer_email=MAINTAINER_EMAIL,
          description=DESCRIPTION,
          license=LICENSE,
          version=VERSION,
          download_url=DOWNLOAD_URL,
          zip_safe=False,  # the package can run out of an .egg file
          platforms='any',
          packages=find_packages(where='saber'),
          package_dir={'': 'saber'},
          install_requires=[
              'mozanalysis'
          ],
          entry_points={'console_scripts': [
              'saber = _command_line:run',
          ]})
