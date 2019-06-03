import os
from typing import Optional

try:
    # This works when the code is executed directly.
    from platform_helper import PlatformHelper
    from output_helper import print_error, print_error_and_exit, print_verbose
except ImportError:
    # This fails when the code is executed directly and not as a part of python package installation,
    # I definitely need a better way to handle this.
    from androide.platform_helper import PlatformHelper
    from androide.output_helper import print_error, print_error_and_exit, print_verbose


class AndroidSdkHelper:

    @staticmethod
    def get_avd_manager_path_uncached() -> Optional[str]:
        binary_name = 'avdmanager'
        binary_paths = [os.path.join('tools', 'bin', 'avdmanager')]
        return AndroidSdkHelper._get_binary(binary_name, binary_paths)

    @staticmethod
    def get_emulator_path_uncached() -> Optional[str]:
        binary_name = 'emulator'
        binary_paths = [
            os.path.join('emulator', 'emulator'),  # New path
            os.path.join('tools', 'emulator')  # Old path
        ]
        return AndroidSdkHelper._get_binary(binary_name, binary_paths)

    @staticmethod
    def get_sdk_manager_path_uncached() -> Optional[str]:
        binary_name = 'sdkmanager'
        binary_paths = [os.path.join('tools', 'bin', 'sdkmanager')]
        return AndroidSdkHelper._get_binary(binary_name, binary_paths)

    @staticmethod
    def _get_binary(binary_name, binary_paths_relative_to_android_sdk) -> str:
        sdk_location = AndroidSdkHelper._get_location_of_android_sdk()
        if not sdk_location:
            print_verbose('ANDROID_SDK_ROOT not defined')
        else:
            for relative_path in binary_paths_relative_to_android_sdk:
                binary_path = os.path.join(sdk_location, relative_path)
                if os.path.exists(binary_path):
                    print_error('\"%s\" found at \"%s\"' % (binary_name, binary_path))
                    return binary_path
                else:
                    print_error('\"%s\" not found at \"%s\"' % (binary_name, binary_path))

        # Only works on Mac and GNU/Linux
        if PlatformHelper.on_linux() or PlatformHelper.on_mac():
            return_code, stdout, stderr = PlatformHelper.execute_cmd('command -v %s' % binary_name)
            if return_code == 0:
                return stdout.strip()
            else:
                print_error('\"%s\" not in path' % binary_name)
        print_error_and_exit('Set ANDROID_SDK_ROOT environment variable to point to Android SDK root')

    @staticmethod
    def _get_location_of_android_sdk() -> Optional[str]:
        return os.environ.get('ANDROID_SDK_ROOT', None)
