#!/usr/local/bin/python3
# Python 2 and 3, print compatibility
from __future__ import print_function

# Without this urllib.parse which is python 3 only cannot be accessed in python 2.
from future.standard_library import install_aliases

install_aliases()

import sys
import os
import docopt


try:
    # This fails when the code is executed directly and not as a part of python package installation,
    # I definitely need a better way to handle this.
    from androide import android_enhanced
    from androide import output_helper
except ImportError:
    # This works when the code is executed directly.
    import android_enhanced
    import output_helper


_VERSION_FILE_NAME = 'version.txt'
_USAGE_STRING = """
A better version of the command-line android tool with a more intuitive command-line interface.

Usage:
    android_enhanced.py [options] doctor
    android_enhanced.py [options] list versions
    android_enhanced.py [options] list others
    android_enhanced.py [options] install version [android-api-version]

Options:
    -v, --verbose       Verbose mode
    
"""


def main():
    args = docopt.docopt(_USAGE_STRING, version=_get_version())
    verbose_mode = args['--verbose']
    output_helper.set_verbose(verbose_mode)
    androide = android_enhanced.AndroidEnhanced()

    if args['doctor']:
        androide.run_doctor()
    else:
        output_helper.print_error_and_exit('Not implemented: "%s"' % ' '.join(sys.argv))


def _get_version():
    dir_of_this_script = os.path.split(__file__)[0]
    version_file_path = os.path.join(dir_of_this_script, _VERSION_FILE_NAME)
    with open(version_file_path, 'r') as fh:
        return fh.read().strip()


if __name__ == '__main__':
    main()

