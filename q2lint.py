# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pathlib
import sys


def main():
    license = pathlib.Path('LICENSE')
    LICENSE = pathlib.Path(__file__).parent / 'LICENSE'

    errors = []
    if license.exists():
        if license.read_text() != LICENSE.read_text():
            errors.append('Invalid LICENSE file')
    else:
        errors.append('Missing LICENSE file')

    for filepath in pathlib.Path('.').glob('**/*.py'):
        if str(filepath).startswith('build/'):
            continue
        if filepath.name in ('_version.py', 'versioneer.py'):
            continue
        with filepath.open('r') as filehandle:
            header = ''.join(line for _, line in zip(range(7), filehandle))
            if header != HEADER:
                errors.append('Invalid header: %s' % filepath)

    if errors:
        sys.exit('\n'.join(errors))


HEADER = """\
# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
"""


if __name__ == '__main__':
    main()
