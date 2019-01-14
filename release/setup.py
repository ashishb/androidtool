from setuptools import setup, find_packages
import os

_DIR_OF_THIS_SCRIPT = os.path.split(__file__)[0]
_VERSION_FILE_NAME = 'version.txt'
_VERSION_FILE_PATH = os.path.join(_DIR_OF_THIS_SCRIPT, 'androide', _VERSION_FILE_NAME)
_README_FILE_NAME = 'README.md'
_README_FILE_PATH = os.path.join(_DIR_OF_THIS_SCRIPT, _README_FILE_NAME)

with open(_VERSION_FILE_PATH, 'r') as fh:
    version = fh.read().strip()

with open(_README_FILE_PATH, 'r') as fh:
    long_description = fh.read()

setup(name='androidtool',
      version=version,
      descaription='A better version of the command-line android SDK manager tool with a more intuitive interface.',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=['Intended Audience :: Developers'],
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Android ADB developer',
      author='Ashish Bhatia',
      author_email='ashishb@ashishb.net',
      url='https://github.com/ashishb/androidtool',
      license='Apache',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'docopt',
          'psutil',
          'typing',
      ],
      entry_points={
          # -*- Entry points: -*-
          'console_scripts': [
              'androidtool=androide.main:main',
          ],
      }
      )
