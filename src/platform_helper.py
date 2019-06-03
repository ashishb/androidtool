import os
import platform
import subprocess

try:
    # This works when the code is executed directly.
    from output_helper import print_verbose
except ImportError:
    # This fails when the code is executed directly and not as a part of python package installation,
    # I definitely need a better way to handle this.
    from androide.output_helper import print_verbose


class PlatformHelper:
    @staticmethod
    def execute_cmd(cmd, cwd=None) -> (int, str, str):
        """
        :param cmd: Command to be executed
        :param cwd: working directory for the command
        :return: (returncode, stdout, stderr)
        """
        if cwd:
            print_verbose('Executing command: \"%s\" using working directory: \"%s\"' % (cmd, cwd))
        else:
            print_verbose('Executing command: \"%s\"' % cmd)
        process = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=os.environ.copy(), cwd=cwd)

        stdout = ''
        stderr = ''

        # Disabled for now, since we lose stdout data due to this indeterministically.
        # while process.poll() is None:
        #     line1 = process.stdout.readline()
        #     line1 = line1.decode('utf-8').strip()
        #     if line1:
        #         stdout += (line1 + '\n')
        #         print_verbose(line1)

        leftover_stdout, leftover_stderr = process.communicate()
        leftover_stdout = leftover_stdout.decode('utf-8').strip()
        leftover_stderr = leftover_stderr.decode('utf-8').strip()
        for line in leftover_stdout.split('\n'):
            line = line.strip()
            if line:
                print_verbose(line)
                stdout += (line + '\n')

        for line in leftover_stderr.split('\n'):
            line = line.strip()
            if line:
                print_verbose(line)
                stderr += (line + '\n')

        return process.returncode, stdout, stderr

    @staticmethod
    def on_linux():
        return platform.system() == 'Linux'

    @staticmethod
    def on_mac():
        return platform.system() == 'Darwin'

    @staticmethod
    def is_64bit_architecture():
        return platform.architecture()[0] == '64bit'
