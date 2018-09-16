# Python 2 and 3, print compatibility
from __future__ import print_function
# Without this urllib.parse which is python 3 only cannot be accessed in python 2.
from future.standard_library import install_aliases

install_aliases()

import psutil
import re
import signal
import subprocess
import sys
import tempfile
import time
import os
import random
from urllib.parse import urlparse
import docopt

try:
    # This fails when the code is executed directly and not as a part of python package installation,
    # I definitely need a better way to handle this.
    from androide.output_helper import print_message, print_error, print_error_and_exit, print_verbose
except ImportError:
    # This works when the code is executed directly.
    from output_helper import print_message, print_error, print_error_and_exit, print_verbose


_JAVA_VERSION_FOR_ANDROID = '1.8'
_JAVA8_INSTALL_COMMAND_FOR_MAC = 'brew cask install caskroom/versions/java8'
_SET_JAVA8_AS_DEFAULT_ON_MAC = 'export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)'


class AndroidEnhanced(object):

    def __init__(self) -> None:
        pass

    def run_doctor(self):
        default_java_version = AndroidEnhanced._get_default_java_version()
        if default_java_version is None:
            print_error_and_exit('Java is not installed. Install Java for Android via %s' %
                                 _JAVA8_INSTALL_COMMAND_FOR_MAC)
        if default_java_version != _JAVA_VERSION_FOR_ANDROID:
            all_java_versions = AndroidEnhanced._get_all_java_versions()
            if _JAVA_VERSION_FOR_ANDROID in all_java_versions:
                print_error_and_exit('Java version %s is installed but default is set to Java %s.\n'
                                     'Set the correct java version via "%s"' % (
                                         _JAVA_VERSION_FOR_ANDROID,
                                         default_java_version,
                                         _SET_JAVA8_AS_DEFAULT_ON_MAC))
            else:
                print_error_and_exit('Java version is %s, Android needs Java %s.\n'
                                     'On Mac install it with "%s"\nAnd then set default version'
                                     'via "%s"' % (
                    default_java_version, _JAVA_VERSION_FOR_ANDROID,_JAVA8_INSTALL_COMMAND_FOR_MAC,
                    _SET_JAVA8_AS_DEFAULT_ON_MAC))
        else:
            print_message('Correct Java version %s is installed' % default_java_version)

    @staticmethod
    def _get_default_java_version() -> str:
        stdout, stderr = AndroidEnhanced._execute_cmd('java -version')
        java_version_regex = '"([0-9]+\.[0-9]+)\..*"'
        version = re.search(java_version_regex, stderr)
        if version is None:
            return None
        return version[1]

    @staticmethod
    def _get_all_java_versions() -> [str]:
        stdout, stderr = AndroidEnhanced._execute_cmd('/usr/libexec/java_home -V')
        java_version_regex = '"([0-9]+\.[0-9]+)\..*"'
        versions = re.findall(java_version_regex, stderr)
        return versions

    @staticmethod
    def _execute_cmd(cmd) -> (str, str):
        ps1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout = ''
        stderr = ''
        for line in ps1.stdout:
            line = line.decode('utf-8').strip()
            stdout += (line + '\n')
        for line in ps1.stderr:
            line = line.decode('utf-8').strip()
            stderr += (line + '\n')

        return stdout, stderr