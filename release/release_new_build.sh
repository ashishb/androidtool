#!/usr/bin/env bash
set -euo pipefail

# Works on both Mac and GNU/Linux.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION_FILENAME=${DIR}/../src/version.txt
SRC_FILES=$(echo -n ${DIR}/../src/{android_sdk_helper.py,main.py,output_helper.py,platform_helper.py,android_enhanced.py,version.txt})

# Open setup file to increment the version
  echo -n "Next the editor will open ${VERSION_FILENAME}, increment the version number in it. Press enter to continue:" &&
  # Wait for a keypress to ensure that user has seen the previous message
  read -n 1 -s &&
  vim ${VERSION_FILENAME} &&
  # Copy the relevant files
  cp ${SRC_FILES} ${DIR}/androide/ &&
  cp ${DIR}/../README.md ${DIR}/README.md &&
  # One time setup
  python3 -m pip install --user --upgrade setuptools wheel twine &&
  # Cleanup before creating the package
  if [ -e "build" ]; then
    rm -r build/
  fi &&
  if [ -e "dist" ]; then
    rm -r dist/
  fi &&
  # Create the package. Reference: https://packaging.python.org/tutorials/packaging-projects/
  python3 setup.py sdist bdist_wheel &&
  # Commit to git before sending package upstream
  git add ${DIR}/../src/version.txt &&
  git commit -m "Setup release $(cat ${VERSION_FILENAME})" &&
  git tag $(cat $VERSION_FILENAME) &&
  git push origin master &&
  git push origin master --tags &&
  # Send the package upstream
  python3 -m twine upload dist/* &&
  echo "Few mins later, check https://pypi.org/project/android-sdk-enhanced/#history to confirm upload" &&
  # Cleanup
  rm -r build/ dist/

# To upload to test network and try:
# rm -r build/ dist/ ; python3 setup.py sdist bdist_wheel && python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# And then install it using
# sudo pip3 install --upgrade --no-cache-dir --index-url https://test.pypi.org/simple/android-sdk-enhanced
