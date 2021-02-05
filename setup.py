# ----------------------------------------------------------------------------
# Copyright (c) 2016-2021, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from setuptools import find_packages, setup

setup(
    name='q2lint',
    version='0.0.1',
    license='BSD-3-Clause',
    url='https://qiime2.org',
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        q2lint=q2lint._main:main
    ''',
    zip_safe=False,
    package_data={'q2lint': ['REF_LICENSE']},
)
