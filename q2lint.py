# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import pathlib
import sys
import glob


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
        with filepath.open('r') as filehandle:
            header = ''.join(line for _, line in zip(range(7), filehandle))
            if header != HEADER:
                errors.append('Invalid header: %s' % filepath)

    npm_packages = filter(lambda x: 'node_modules' not in x,
                          glob.glob('**/*/package.json', recursive=True))
    if npm_packages:
        import subprocess
        import os

        for package in npm_packages:
            pkg_path, _ = os.path.split(package)
            cmd = 'cd %s; npm i; npm run build; git diff --quiet */bundle.js' \
                  ' || bash -c "exit -1"; git checkout -- .' % pkg_path
            if subprocess.run(cmd, shell=True).returncode != 0:
                errors.append('npm build error on %s' % pkg_path)

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
