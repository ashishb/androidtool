import os
import re
from typing import Optional

try:
    # This works when the code is executed directly.
    from android_sdk_helper import AndroidSdkHelper
    from platform_helper import PlatformHelper
    from output_helper import print_message, print_error, print_error_and_exit, print_verbose
except ImportError:
    # This fails when the code is executed directly and not as a part of python package installation,
    # I definitely need a better way to handle this.
    from androide.output_helper import print_message, print_error, print_error_and_exit, print_verbose
    from androide.android_sdk_helper import AndroidSdkHelper
    from androide.platform_helper import PlatformHelper


_JAVA_VERSION_FOR_ANDROID = '1.8'
_JAVA8_INSTALL_COMMAND_FOR_MAC = 'brew cask install caskroom/versions/java8'
_SET_JAVA8_AS_DEFAULT_ON_MAC = 'export JAVA_HOME=$(/usr/libexec/java_home -v 1.8)'
_GET_ALL_JAVA_VERSIONS_ON_MAC = '/usr/libexec/java_home -V'
_GET_ALL_JAVA_VERSIONS_ON_LINUX = 'update-alternatives --display java'

_BUILD_TOOLS_REGEX = r'build-tools;\S*'
_SYSTEM_IMAGES_REGEX = 'system-images;android-([0-9]+);(.*);(.*)\n'


class AndroidEnhanced:

    def __init__(self) -> None:
        # Initialize to None
        self._avd_manager = None
        self._emulator = None
        self._sdk_manager = None

    def run_doctor(self) -> None:
        print_message('Checking java version...')
        self._ensure_correct_java_version()
        print_message('Checking SDK manager is installed...')
        self._ensure_sdkmanager_is_installed()
        print_message('Checking that basic Android packages are installed...')
        if not self._ensure_basic_packages_are_installed():
            print_error_and_exit('Not all basic packages are installed')
    
    def _ensure_basic_packages_are_installed(self) -> bool:
        success = True
        installed_packages = self._get_installed_packages()
        basic_packages = self._get_basic_packages()
        num_packages = len(basic_packages)
        for i in range(0, num_packages):
            basic_package = basic_packages[i]
            if basic_package not in installed_packages:
                print_error('Basic packages \"%s\" is not installed' % basic_package)
                success = False
            else:
                print_message('Package %d/%d: \"%s\" is installed' % (i + 1, num_packages, basic_package))

        return success

    def list_packages(self, arch=None, api_type=None) -> None:
        print_verbose('List packages(arch: %s, api_type: %s)' % (arch, api_type))
        if api_type is None:
            google_api_type = '.*?'
        else:
            google_api_type = api_type

        if arch is None:
            arch_pattern = '.*?'
        else:
            arch_pattern = arch + '.*?'
        regex_pattern = 'system-images;android-([0-9]+);(%s);(%s)\n' % (google_api_type, arch_pattern)
        print_verbose('Package pattern: %s' % regex_pattern)
        return_code, stdout, stderr = PlatformHelper.execute_cmd(
            '%s --verbose --list --include_obsolete' % self._get_sdk_manager_path())
        if return_code != 0:
            print_error_and_exit('Failed to list packages (return code: %d)' % return_code)
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

        for (google_api_type, architectures) in arch_to_android_version_map.items():
            if google_api_type == 'default':
                print('Google API type: default (Standard Android image; no Google API)')
            else:
                print('Google API type: %s' % google_api_type)
            for architecture in architectures:
                android_api_versions = arch_to_android_version_map[google_api_type][architecture]
                print('%s -> %s' % (architecture, ', '.join(android_api_versions)))
            print()

    def list_installed_packages(self):
        installed_packages = self._get_installed_packages()
        if installed_packages:
            print('\n'.join(installed_packages))
        else:
            print_error('No installed packages found')

    def list_avds(self):
        avd_manager = self._get_avd_manager_path()
        if not avd_manager:
            print_error_and_exit('avdmanager not found')
        cmd = '%s --verbose list avd' % avd_manager
        return_code, stdout, stderr = PlatformHelper.execute_cmd(cmd)
        if return_code != 0:
            print_error_and_exit('Failed to execute avdmanager')
        start = stdout.find('Virtual Devices')
        if start != -1:
            stdout = stdout[start:]
        print(stdout)

    def install_api_version(self, version, arch=None, api_type=None) -> None:
        platform_package = self._get_platform_package(version)
        sources_package = self._get_sources_package(version)
        addons_package = self._get_add_ons_package(version, api_type)
        system_images_package = self._get_system_images_package(version, arch, api_type)

        package_list = list()
        package_list.append(platform_package)
        if sources_package:
            package_list.append(sources_package)
        if addons_package:
            package_list.append(addons_package)
        if system_images_package:
            package_list.append(system_images_package)
        if not self._install_sdk_packages(package_list):
            print_error_and_exit('Failed to install packages for api version: %s' % version)

    def list_build_tools(self):
        build_tools = self._get_build_tools()
        for build_tool in build_tools:
            print(build_tool)

    def list_others(self):
        cmd = '%s --verbose --list --include_obsolete' % self._get_sdk_manager_path()
        return_code, stdout, stderr = PlatformHelper.execute_cmd(cmd)
        if return_code != 0:
            print_error_and_exit('Failed to list packages')

        print('Installed Packages:')
        lines = stdout.split('\n')
        for (i, line) in enumerate(lines):
            line = line.strip()
            previous_line = None
            if i > 0:
                previous_line = lines[i - 1].strip()

            is_package_name = not previous_line or previous_line.startswith('---')

            if not is_package_name:
                continue

            print_verbose('Line is \"%s\" and previous line is \"%s\"' % (line, previous_line))

            if not line:
                continue
            elif line.startswith('system-images;') or line.startswith('platforms;') or line.startswith('sources;'):
                continue
            elif line.startswith('platform-tools'):
                continue
            elif line.startswith('build-tools;'):
                continue
            elif line.find('Info:') != -1:
                continue

            if line.endswith(':'):
                print('')
            print(line)

    def install_basic_packages(self):
        packages_to_install = self._get_basic_packages()
        if not self._install_sdk_packages(packages_to_install):
            print_error_and_exit('Failed to install basic packages')

    def update_all(self):
        cmd = '%s --update' % self._get_sdk_manager_path()
        return_code, stdout, stderr = PlatformHelper.execute_cmd(cmd)
        if return_code != 0:
            print_error_and_exit('Failed to update, return code: %d' % return_code)
        count = 0
        if stdout:
            for line in stdout.split('\r'):
                if line.find('Fetch remote repository'):
                    continue
                else:
                    count += 1
        if count == 0:
            print_message('No packages to update')
            self._accept_all_licenses()
        else:
            print_message(stdout)

    def create_avd(self, avd_name, api_version, arch, api_type):
        if api_type is None:
            api_type = 'google_apis'  # Preferred
        if arch is None:
            if PlatformHelper.is_64bit_architecture():
                arch = 'x86_64'
            else:
                arch = 'x86'
        package_name = AndroidEnhanced._get_system_images_package(api_version, arch, api_type)
        print_verbose('Package is %s' % package_name)
        self.install_api_version(api_version, arch=arch, api_type=api_type)
        # Say no to custom hardware profile.
        print_message('Creating AVD "%s" of type "%s" ' % (avd_name, package_name))
        create_cmd = 'echo no | %s --verbose create avd --name %s --package "%s"' % (
            self._get_avd_manager_path(), avd_name, package_name)
        return_code, stdout, stderr = PlatformHelper.execute_cmd(create_cmd)
        if return_code != 0:
            print_error('Failed to create AVD')
            print_error('stdout: %s' % stdout)
            print_error_and_exit('stderr: %s' % stderr)
        print_message('AVD \"%s\" created successfully' % avd_name)

    def start_avd(self, avd_name, headless_mode, verbose_mode):
        # cmd = '%s -avd %s -no-boot-anim -no-skin' % (self._get_emulator_path(), avd_name)
        cmd = '%s -avd %s -no-boot-anim' % ('./emulator', avd_name)
        if headless_mode:
            cmd = '%s -no-window' % cmd.strip()
        if verbose_mode:
            cmd = '%s -verbose' % cmd.strip()
        return_code, stdout, stderr = PlatformHelper.execute_cmd(cmd, cwd=os.path.dirname(self._get_emulator_path()))
        if return_code != 0:
            print_error('Failed to start emulator\nstdout:\n' + stdout + '\n\nstderr:\n' + stderr)
            print_message('List of valid virtual devices')
            self.list_avds()

    @staticmethod
    def _ensure_correct_java_version():
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
                                         default_java_version, _JAVA_VERSION_FOR_ANDROID,
                                         _JAVA8_INSTALL_COMMAND_FOR_MAC, _SET_JAVA8_AS_DEFAULT_ON_MAC))
        else:
            print_message('Correct Java version %s is installed' % default_java_version)

    def _ensure_sdkmanager_is_installed(self):
        if not self._get_sdk_manager_path():
            print_error_and_exit('sdkamanger not found, is Android SDK installed?')

    def _accept_all_licenses(self):
        cmd = 'yes | %s --licenses' % self._get_sdk_manager_path()
        return_code, stdout, stderr = PlatformHelper.execute_cmd(cmd)
        if return_code != 0:
            print_error_and_exit('Failed to accept licenses, return code: %d' % return_code)
        license_regex = '([0-9]*) of ([0-9]*) SDK package licenses not accepted'
        result = re.search(license_regex, stdout)
        if result is None:
            print_message('All licenses accepted')
        else:
            print_message('%d of %d licenses accepted' % (int(result.group(1)), int(result.group(2))))

    @staticmethod
    def _get_default_java_version() -> Optional[str]:
        return_code, stdout, stderr = PlatformHelper.execute_cmd('java -version')
        if return_code != 0:
            print_error('Failed to get java version')
            return None
        # TODO(ashishb): Do I need two different regex for Mac and Linux like _get_all_java_versions here?
        java_version_regex = r'"([0-9]+\.[0-9]+)\..*"'
        version = re.search(java_version_regex, stderr)
        if version is None:
            return None
        print_verbose('version object is %s' % version)
        return version.group(1)

    @staticmethod
    def _get_all_java_versions() -> [str]:
        if PlatformHelper.on_linux():
            return_code, stdout, stderr = PlatformHelper.execute_cmd(_GET_ALL_JAVA_VERSIONS_ON_LINUX)
            java_version_regex = 'java-([0-9]+.*?)/'
        elif PlatformHelper.on_mac():
            java_version_regex = r'"([0-9]+\.[0-9]+)\..*"'
            return_code, stdout, stderr = PlatformHelper.execute_cmd(_GET_ALL_JAVA_VERSIONS_ON_MAC)
        else:
            print_error('Unsupported operating system')
            return []

        if return_code != 0:
            print_error('Failed to list java versions')
            return []
        output = ''
        output += stdout
        output += stderr
        versions = re.findall(java_version_regex, output)
        versions = set(versions)
        print_verbose('Versions are %s' % versions)
        return versions
    
    def _get_installed_packages(self) -> [str]:
        cmd = '%s --verbose --list --include_obsolete' % self._get_sdk_manager_path()
        return_code, stdout, stderr = PlatformHelper.execute_cmd(cmd)
        if return_code != 0:
            print_error('Failed to list packages')
            return None

        start_line = 'Installed packages:'.lower()
        end_line = 'Available Packages:'.lower()
        lines = stdout.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.lower().find(start_line) != -1:
                i += 1
                break
            else:
                i += 1
        installed_packages = set()
        for j in range(i, len(lines)):
            line = lines[j]
            if line.lower().find(end_line) != -1:
                break
            line = line.strip()
            if not line:
                continue

            if line.startswith('----'):
                continue
            if line.startswith('Description:'):
                continue
            if line.startswith('Version:'):
                continue
            if line.startswith('Installed Location:'):
                continue
            if line.startswith('Installed Obsolete Packages:'):
                continue
            installed_packages.add(line)
        return sorted(installed_packages)

    def _get_build_tools(self) -> [str]:
        """
        :return: List of build tools packages, sorted by version number, latest package comes last
        """
        cmd = '%s --verbose --list --include_obsolete' % self._get_sdk_manager_path()
        return_code, stdout, stderr = PlatformHelper.execute_cmd(cmd)
        if return_code != 0:
            print_error_and_exit('Failed to list build tools, stdout: %s, stderr: %s' % (stdout, stderr))
        build_tools = re.findall(_BUILD_TOOLS_REGEX, stdout)
        build_tools = sorted(set(build_tools))
        print_verbose('Build tools are %s' % build_tools)
        return build_tools

    def _get_basic_packages(self) -> [str]:
        build_tools = self._get_build_tools()
        if not build_tools:
            print_error_and_exit('Build tools list is empty, this is unexpected')
        latest_build_package = build_tools[-1]
        print_verbose('Latest build package is \"%s\"' % latest_build_package)
        packages_to_install = [
            latest_build_package,
            'emulator',
            'tools',
            'platform-tools',
            'extras;android;m2repository',
            'extras;google;m2repository',
            'patcher;v4',
        ]
        # HAXM is not required on Linux. It is required on Windows and OSX.
        # I am assuming that this tool will never run on anything except Windows and OSX.
        # I don't know whether HAXM is required on BSD or not.
        if not PlatformHelper.on_linux():
            packages_to_install.append('extras;intel;Hardware_Accelerated_Execution_Manager')
        return packages_to_install

    @staticmethod
    def _get_platform_package(version) -> str:
        return 'platforms;android-%s' % version

    @staticmethod
    def _get_sources_package(version) -> Optional[str]:
        try:
            version = int(version)
            if version < 14:
                print_error('Sources are not available before API 14')
                return None
        except ValueError:
            pass

        return 'sources;android-%s' % version

    @staticmethod
    def _get_add_ons_package(version, api_type) -> Optional[str]:
        # addons package is gone going forward. It was present only on these versions.
        if api_type == 'google_apis' and version in [15, 16, 17, 18, 19, 21, 22, 23, 24]:
            return 'add-ons;addon-google_apis-google-%s' % version
        # Note: There are two more packages types, GDK for Glass and Google TV which is deprecated.
        # No point, supporting them here.
        # add-ons;addon-google_gdk-google-19
        # add-ons;addon-google_tv_addon-google-12
        # add-ons;addon-google_tv_addon-google-13
        return None

    @staticmethod
    def _get_system_images_package(version, arch, api_type) -> Optional[str]:
        try:
            version = int(version)
            if version < 10:
                print_verbose('System images are bundled in the platform below API 10')
                return None
            # API 24 onwards, for x86, prefer to install google_apis_playstore image
            # then google_apis image. It seems it is a better image.
            if version >= 24 and api_type == 'google_apis' and arch == 'x86':
                api_type = 'google_apis_playstore'
                return 'system-images;android-%s;%s;%s' % (version, api_type, arch)
            # API 28 onwards, for x86_64, prefer to install google_apis_playstore image
            # then google_apis image. It seems it is a better image.
            if version >= 28 and api_type == 'google_apis' and arch == 'x86_64':
                api_type = 'google_apis_playstore'
                return 'system-images;android-%s;%s;%s' % (version, api_type, arch)
        except ValueError:
            pass
        return 'system-images;android-%s;%s;%s' % (version, api_type, arch)

    def _install_sdk_packages(self, package_names) -> bool:
        for package_name in package_names:
            exists = self._does_package_exist(package_name)
            if not exists:
                print_message('Package \"%s\" not found' % package_name)
                return False

        print_message('Installing packages [%s]...' % ', '.join(package_names))
        package_names_str = '\"' + '\" \"'.join(package_names) + '\"'
        cmd = 'yes | %s --verbose %s' % (self._get_sdk_manager_path(), package_names_str)
        return_code, stdout, stderr = PlatformHelper.execute_cmd(cmd)
        if return_code != 0:
            print_error('Failed to install packages \"%s\"' % ' '.join(package_names))
            print_error('Stderr is \n%s' % stderr)
            return False
        return True

    def _get_avd_manager_path(self) -> Optional[str]:
        """
        :return: path to avdmanager binary, caches the result for the future use.
        """
        if not self._avd_manager:
            self._avd_manager = AndroidSdkHelper.get_avd_manager_path_uncached()
            print_verbose('avdmanager is located at %s' % self._avd_manager)

        # Return the cached value
        return self._avd_manager

    def _get_sdk_manager_path(self) -> Optional[str]:
        """
        :return: path to sdkmanager binary, caches the result for the future use.
        """
        if not self._sdk_manager:
            self._sdk_manager = AndroidSdkHelper.get_sdk_manager_path_uncached()
            print_verbose('sdkmanager is located at %s' % self._sdk_manager)
        # Return the cached value
        return self._sdk_manager

    def _get_emulator_path(self):
        """
        :return: Path to Android emulator binary, caches the result for the future use.
        """
        if not self._emulator:
            self._emulator = AndroidSdkHelper.get_emulator_path_uncached()
            print_verbose('Emulator is located at %s' % self._emulator)
        # Return the cached value
        return self._emulator

    # TODO(ashishb): Implement this in the future to check whether a package is available or not.
    #pylint: disable=W0613
    def _does_package_exist(self, package_name):
        return True