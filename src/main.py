#!/usr/local/bin/python3

import sys
import os
from typing import Optional

import docopt


def _using_python2():
    return sys.version_info < (3, 0)


# This code does not support Python 2
assert not _using_python2(), 'You are using Python 2 which is not supported. Use Python 3.'

try:
    # This works when the code is executed directly.
    import android_enhanced
    import output_helper
except ImportError:
    # This fails when the code is executed directly and not as a part of python package installation,
    # I definitely need a better way to handle this.
    from androide import android_enhanced
    from androide import output_helper

_VERSION_FILE_NAME = 'version.txt'
_USAGE_STRING = """
A better version of the command-line android tool with a more intuitive command-line interface.

Usage:
    androidtool [options] doctor
    androidtool [options] list build tools
    androidtool [options] list installed packages
    androidtool [options] list api versions [--x86_64 | --x86 | --arm] [--google-apis | --no-google-apis | --android-tv | --android-wear] 
    androidtool [options] list other packages
    androidtool [options] install basic packages
    androidtool [options] install version <android-api-version> [--x86_64 | --x86 | --arm] [--google-apis | --no-google-apis | --android-tv | --android-wear]
    androidtool [options] update all
    androidtool [options] list avds
    androidtool [options] create avd <avd-name> <android-api-version> [--x86_64 | --x86 | --arm] [--google-apis | --no-google-apis | --android-tv | --android-wear]
    androidtool [options] start avd <avd-name> [--headless]

Options:
    -v, --verbose       Verbose mode
    
    
Sub-command description:
    doctor - ensures that you have right version of Java. In the future, it will check Android SDK installation as well.
    list build tools - lists available build tools
    list api versions - lists different SDK versions available to install
    list other packages - lists packages apart from build tools and api versions
    list installed packages - lists installed packages
    list avds - lists setup AVDs
    install basic tools - installs a basic set of tools. Highly recommended to run it the first time.
    install version - installs a particular API version
    update all - updates all installed packages to the latest versions.
    create avd - creates a new AVD. It will install the package, if required. By default, Google API build with X86_64 (on 64-bit) and X86 on 32-bit will be created.
    start avd - Starts an existing AVD.
    
androidtool relies on using ANDROID_SDK_ROOT environment variable to find the Android SDK or expects sdkamanger, 
avdmanager, and emulator commands to be in the path.
"""


def main():
    args = docopt.docopt(_USAGE_STRING, version=_get_version())
    verbose_mode = args['--verbose']
    output_helper.set_verbose(verbose_mode)
    androide = android_enhanced.AndroidEnhanced()

    if args['doctor']:
        androide.run_doctor()
    elif args['list'] and args['api'] and args['versions']:
        arch = get_architecture(args)
        api_type = get_api_type(args)
        androide.list_packages(arch, api_type)
    elif args['install'] and args['version']:
        arch = get_architecture(args)
        api_type = get_api_type(args)
        if api_type is None:
            api_type = 'default'
        if arch is None:
            arch = 'x86'
        version = args['<android-api-version>']
        androide.install_api_version(version, arch, api_type)
    elif args['list'] and args['build'] and args['tools']:
        androide.list_build_tools()
    elif args['list'] and args['other'] and args['packages']:
        androide.list_others()
    elif args['list'] and args['installed'] and args['packages']:
        androide.list_installed_packages()
    elif args['update'] and args['all']:
        androide.update_all()
    elif args['install'] and args['basic'] and args['packages']:
        androide.install_basic_packages()
    elif args['list'] and args['avds']:
        androide.list_avds()
    elif args['create'] and args['avd']:
        name = args['<avd-name>']
        api_version = args['<android-api-version>']
        api_type = get_api_type(args)
        arch = get_architecture(args)
        androide.create_avd(name, api_version, arch, api_type)
    elif args['start'] and args['avd']:
        # To be implemented
        name = args['<avd-name>']
        headless_mode = args['--headless']
        androide.start_avd(name, headless_mode, verbose_mode)
    else:
        output_helper.print_error_and_exit('Not implemented: "%s"' % ' '.join(sys.argv))


def get_api_type(args) -> Optional[str]:
    api_type = None  # default
    if args['--no-google-apis']:
        api_type = 'default'
    elif args['--google-apis']:
        api_type = 'google_apis'
    elif args['--android-tv']:
        api_type = 'android-tv'
    elif args['--android-wear']:
        api_type = 'android-wear'
    return api_type


def get_architecture(args) -> Optional[str]:
    arch = None  # default
    if args['--x86']:
        arch = 'x86'
    elif args['--arm']:
        arch = 'armeabi-v7a'
    elif args['--x86_64']:
        arch = 'x86_64'
    return arch


def _get_version():
    dir_of_this_script = os.path.split(__file__)[0]
    version_file_path = os.path.join(dir_of_this_script, _VERSION_FILE_NAME)
    with open(version_file_path, 'r') as fh:
        return fh.read().strip()


if __name__ == '__main__':
    main()

