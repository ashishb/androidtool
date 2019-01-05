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
        # Only works on Mac and GNU/Linux
        if PlatformHelper.on_linux() or PlatformHelper.on_mac():
            return_code, stdout, stderr = PlatformHelper.execute_cmd('command -v avdmanager')
            if return_code == 0:
                return 'avdmanager'
            else:
                print_verbose('avdmanager not in path, checking for ANDROID_SDK_ROOT')

        sdk_location = AndroidSdkHelper._get_location_of_android_sdk()
        if not sdk_location:
            print_error('Unable to find Android SDK')
            return None

        avd_manager_path = os.path.join(sdk_location, 'tools', 'bin', 'avdmanager')
        if os.path.exists(avd_manager_path):
            return avd_manager_path
        else:
            print_error_and_exit('avdmanager not found at \"%s\"' % avd_manager_path)
            return None

    @staticmethod
    def get_emulator_path_uncached() -> Optional[str]:
        # Only works on Mac and GNU/Linux
        if PlatformHelper.on_linux() or PlatformHelper.on_mac():
            return_code, stdout, stderr = PlatformHelper.execute_cmd('command -v emulator')
            if return_code == 0:
                return 'emulator'
            else:
                print_verbose('emulator not in path, checking for ANDROID_SDK_ROOT')

        sdk_location = AndroidSdkHelper._get_location_of_android_sdk()
        if not sdk_location:
            print_error('Unable to find Android SDK')
            return None

        # New SDK path
        emulator_path = os.path.join(sdk_location, 'emulator', 'emulator')
        if os.path.exists(emulator_path):
            return emulator_path
        else:
            print_error('emulator not found at \"%s\", looking for an alternative...' % emulator_path)

        # Old SDK path
        emulator_path = os.path.join(sdk_location, 'tools', 'emulator')
        if os.path.exists(emulator_path) and os.path.isfile(emulator_path):
            return emulator_path
        else:
            print_error('emulator not found at \"%s\"' % emulator_path)

        print_error_and_exit('emulator not found')

    @staticmethod
    def get_sdk_manager_path_uncached() -> Optional[str]:
        # Only works on Mac and GNU/Linux
        if PlatformHelper.on_linux() or PlatformHelper.on_mac():
            return_code, stdout, stderr = PlatformHelper.execute_cmd('command -v sdkmanager')
            if return_code == 0:
                return 'sdkmanager'
            else:
                print_verbose('sdkmanager not in path, checking for ANDROID_SDK_ROOT')

        sdk_location = AndroidSdkHelper._get_location_of_android_sdk()
        if not sdk_location:
            print_error('Unable to find Android SDK')
            return None

        sdk_manager_path = os.path.join(sdk_location, 'tools', 'bin', 'sdkmanager')
        if os.path.exists(sdk_manager_path):
            return sdk_manager_path
        else:
            print_error_and_exit('sdkmanager not found at \"%s\"' % sdk_manager_path)
            return None

    @staticmethod
    def _get_location_of_android_sdk() -> Optional[str]:
        try:
            return os.environ['ANDROID_SDK_ROOT']
        except KeyError:
            print_error_and_exit(
                'Set ANDROID_SDK_ROOT environment variable to point to Android SDK root')
