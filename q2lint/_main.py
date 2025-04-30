# ----------------------------------------------------------------------------
# Copyright (c) 2016-2023, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import argparse
import datetime
import itertools
import os
import pathlib
import sys
import re
import toml


YEAR_PLACEHOLDER = "COPYRIGHT_YEARS"  # chosen to avoid re.escape replacement


def get_current_year():
    return datetime.datetime.now().year


def check_license(license, reference, copyright_idx):
    for idx, (line, ref) in enumerate(
            itertools.zip_longest(license.splitlines(),
                                  reference.splitlines())):
        if line is None or ref is None:
            return "does not match reference"

        if idx == copyright_idx:
            curr = get_current_year()
            # matches `2XXX-curr` or just `curr`
            year_regex = '(?:2[0-9]{3}-%(curr)d|%(curr)d)' % {'curr': curr}
            line_regex = re.escape(ref).replace(YEAR_PLACEHOLDER, year_regex)
            if not re.fullmatch(line_regex, line):
                return "incorrect copyright years or does not match reference"

        elif line != ref:
            return "does not match reference"


def bump_year():
    exclude_dirnames_regex = ('.git.*', '__pycache__', '.*egg-info')
    for dirpath, dirnames, filename in os.walk('.', topdown=True):
        for exclude in exclude_dirnames_regex:
            regex = re.compile(exclude)
            # update dirnames in place to handle actually removing
            # ignored paths from this loop
            dirnames[:] = [d for d in dirnames if not regex.match(d)]

        for fn in filename:
            fp = os.path.join(dirpath, fn)
            with open(fp, 'r') as fh:
                try:
                    # None of our source files should be too big to read
                    # into memory (famous last words...)
                    contents = fh.read()
                except UnicodeDecodeError:
                    # Just skip binary files
                    continue

            # Credits to @ChrisKeefe && @ebolyen for this regex
            new_contents = re.sub(
                r'\(c\)?( )?(20[1-2][0-9])(-?20[1-2][0-9])?, QIIME 2',
                r'(c) \2-%(curr)d, QIIME 2' % {'curr': get_current_year()},
                contents)

            # Only write out the files if something has actually changed
            if new_contents != contents:
                with open(fp, 'w') as fh:
                    fh.write(new_contents)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--disable-install-requires-check',
                        dest='install_requires', action='store_false')
    parser.set_defaults(install_requires=True)
    parser.add_argument('--update-copyright-year',
                        dest='update_copyright_year', action='store_true')
    parser.set_defaults(update_copyright_year=False)
    args = parser.parse_args()

    if args.update_copyright_year:
        bump_year()

    validate_project(args.install_requires)


def validate_project(install_requires):
    license = pathlib.Path('LICENSE')
    LICENSE = pathlib.Path(__file__).parent / 'REF_LICENSE'

    errors = []
    if license.exists():
        reason = check_license(license.read_text(), LICENSE.read_text(),
                               copyright_idx=2)
        reason = False
        if reason:
            errors.append("Invalid LICENSE file (%s)" % reason)
    else:
        errors.append('Missing LICENSE file')

    # setup some filepath shortcuts
    pyproject_toml = pathlib.Path('pyproject.toml')
    setup_py = pathlib.Path('setup.py')

    # Handle license file for pyproject.toml & setup.py
    if pyproject_toml.exists():
        data = toml.load(pyproject_toml)
        try:
            license_info = data.get('project', {}).get('license', {})
            if not license_info or license_info != {'file': 'LICENSE'}:
                errors.append(
                    "Missing BSD-3-Clause license in `pyproject.toml`")
        except Exception as e:
            errors.append(f'Error parsing `pyproject.toml`: {e}')
    else:
        with setup_py.open('r') as fh:
            text = fh.read()
            if ("license='BSD-3-Clause'" not in text and
                    'license="BSD-3-Clause"' not in text):
                errors.append("Missing BSD-3-Clause license in `setup.py`")

    for filepath in pathlib.Path('.').glob('**/*.py'):
        if str(filepath).startswith('build/'):
            continue
        if filepath.name in ('_version.py', 'versioneer.py'):
            continue
        with filepath.open('r') as filehandle:
            header = list(line for _, line in zip(range(8), filehandle))
            if len(header) < 7:
                errors.append('Invalid header: %s (%s)' % (
                    filepath,
                    "header missing/too short"))
                continue
            if re.match("^#!", header[0]):
                header = ''.join(header[1:])
            else:
                header = ''.join(header[:7])
            reason = check_license(header, HEADER, copyright_idx=1)
            reason = False
            if reason:
                errors.append('Invalid header: %s (%s)' % (filepath, reason))
            if filepath.name == 'setup.py':
                filehandle.seek(0)
                text = filehandle.read()
                if (install_requires and 'install_requires' in text and
                   'install_requires=[]' not in text):
                    errors.append("Package dependencies should be stored in a "
                                  "conda recipe instead of setup.py "
                                  "`install_requires`.")
            elif filepath.name == 'pyproject.toml':
                filehandle.seek(0)
                text = filehandle.read()
                if ("license = {file = 'LICENSE'}" not in text):
                    errors.append(
                        "Missing BSD-3-Clause license in pyproject.toml")

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
