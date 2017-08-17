# ----------------------------------------------------------------------------
# Copyright (c) 2016-2017, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import itertools
import argparse
import datetime
import pathlib
import sys
import re


YEAR_PLACEHOLDER = "COPYRIGHT_YEARS"  # chosen to avoid re.escape replacement


def check_license(license, reference, copyright_idx):
    for idx, (line, ref) in enumerate(
            itertools.zip_longest(license.splitlines(),
                                  reference.splitlines())):
        if idx == copyright_idx and line is not None:
            curr = datetime.datetime.now().year
            # matches `2XXX-curr` or just `curr`
            year_regex = '(?:2[0-9]{3}-%(curr)d|%(curr)d)' % {'curr': curr}
            line_regex = re.escape(ref).replace(YEAR_PLACEHOLDER, year_regex)
            if not re.fullmatch(line_regex, line):
                return "incorrect copyright years or does not match reference"

        elif line != ref:
            return "does not match reference"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disable-install-requires-check',
                        dest='install_requires', action='store_false')
    parser.set_defaults(install_requires=True)
    args = parser.parse_args()

    license = pathlib.Path('LICENSE')
    LICENSE = pathlib.Path(__file__).parent / 'REF_LICENSE'

    errors = []
    if license.exists():
        reason = check_license(license.read_text(), LICENSE.read_text(),
                               copyright_idx=2)
        if reason:
            errors.append("Invalid LICENSE file (%s)" % reason)
    else:
        errors.append('Missing LICENSE file')

    for filepath in pathlib.Path('.').glob('**/*.py'):
        if str(filepath).startswith('build/'):
            continue
        if filepath.name in ('_version.py', 'versioneer.py'):
            continue
        with filepath.open('r') as filehandle:
            header = ''.join(line for _, line in zip(range(7), filehandle))
            reason = check_license(header, HEADER, copyright_idx=1)
            if reason:
                errors.append('Invalid header: %s (%s)' % (filepath, reason))
            if filepath.name != 'setup.py':
                continue
            text = filehandle.read()
            if (args.install_requires and 'install_requires' in text and
               'install_requires=[]' not in text):
                errors.append("Package dependencies should be stored in a "
                              "conda recipe instead of setup.py "
                              "`install_requires`.")
            if ("license='BSD-3-Clause'" not in text and
               'license="BSD-3-Clause"' not in text):
                errors.append("Missing BSD-3-Clause license in setup.py")

    npm_packages = filter(lambda x: 'node_modules' not in str(x),
                          pathlib.Path('.').glob('**/*/package.json'))
    if npm_packages:
        import subprocess

        for package in npm_packages:
            pkg_path = package.parent
            install = 'cd %s && npm i --silent --progress false' % pkg_path
            cmd = subprocess.run(install, shell=True,
                                 stdout=subprocess.DEVNULL)
            if cmd.returncode != 0:
                errors.append('npm install failed')
            cmd = 'cd %s && npm run build -- --bail && (git diff ' \
                  '--quiet */bundle.js || bash -c "exit 42")' % pkg_path
            res = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL)
            if res.returncode == 42:
                errors.append('Bundle is out of sync for %s' % pkg_path)
            elif res.returncode != 0:
                errors.append('npm build error on %s' % pkg_path)

    if errors:
        sys.exit('\n\n\033[91m%s\033[0m\n\n' % '\n'.join(errors))


HEADER = """\
# ----------------------------------------------------------------------------
# Copyright (c) COPYRIGHT_YEARS, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
"""


if __name__ == '__main__':
    main()
