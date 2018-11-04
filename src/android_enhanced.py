import platform
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
from typing import Optional
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
_GET_ALL_JAVA_VERSIONS_ON_MAC = '/usr/libexec/java_home -V'
_GET_ALL_JAVA_VERSIONS_ON_LINUX = 'update-alternatives --display java'


class AndroidEnhanced(object):

    def __init__(self) -> None:
        pass

    def run_doctor(self) -> None:
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

    def list_packages(self, arch=None, api_type=None) -> None:
        print_verbose('List packages(arch: %s, api_type: %s)' % (arch, api_type))
        if api_type is None:
            google_api_type = '.*?'
        else:
            google_api_type = 'api_type'

        if arch is None:
            arch_pattern = '.*?'
        else:
            arch_pattern = arch + '.*?'
        regex_pattern = 'system-images;android-([0-9]+);(%s);(%s)\n' % (google_api_type, arch_pattern)
        stdout, stderr = self._execute_cmd('sdkmanager --verbose --list --include_obsolete')
        system_images = re.findall(regex_pattern, stdout)
        arch_to_android_version_map = {}
        for system_image in system_images:
            android_api_version = system_image[0]
            google_api_type = system_image[1]
            arch = system_image[2]
            if google_api_type not in arch_to_android_version_map:
                arch_to_android_version_map[google_api_type] = {}
            if arch not in arch_to_android_version_map[google_api_type]:
                arch_to_android_version_map[google_api_type][arch] = []
            arch_to_android_version_map[google_api_type][arch].append(android_api_version)

        for (google_api_type, archictures) in arch_to_android_version_map.items():
            print('Google API type: %s' % google_api_type)
            for arch in archictures:
                android_api_versions = arch_to_android_version_map[google_api_type][arch]
                print('%s -> %s' % (arch, ', '.join(android_api_versions)))
            print()

    def list_build_tools(self):
        regex_pattern = 'build-tools.*'
        stdout, stderr = self._execute_cmd('sdkmanager --verbose --list --include_obsolete')
        build_tools = re.findall(regex_pattern, stdout)
        for build_tool in build_tools:
            print(build_tool)

    @staticmethod
    def _get_default_java_version() -> Optional[str]:
        stdout, stderr = AndroidEnhanced._execute_cmd('java -version')
        java_version_regex = '"([0-9]+\.[0-9]+)\..*"'
        version = re.search(java_version_regex, stderr)
        if version is None:
            return None
        print_verbose('version object is %s' % version)
        return version.group(1)

    @staticmethod
    def _get_all_java_versions() -> [str]:
        if AndroidEnhanced._on_linux():
            stdout, stderr = AndroidEnhanced._execute_cmd(_GET_ALL_JAVA_VERSIONS_ON_LINUX)
            java_version_regex = 'java-([0-9]+.*?)/'
        elif AndroidEnhanced._on_mac():
            java_version_regex = '"([0-9]+\.[0-9]+)\..*"'
            stdout, stderr = AndroidEnhanced._execute_cmd(_GET_ALL_JAVA_VERSIONS_ON_MAC)
        else:
            return []
        output = ''
        output += stdout
        output += stderr
        versions = re.findall(java_version_regex, output)
        versions = set(versions)
        print_verbose('Versions are %s' % versions)
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

        print_verbose(stdout)
        print_verbose(stderr)
        return stdout, stderr

    @staticmethod
    def _on_linux():
        return platform.system() == 'Linux'

    @staticmethod
    def _on_mac():
        return platform.system() == 'Darwin'