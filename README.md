# Android SDK Enhanced [![Downloads](https://pepy.tech/badge/android-sdk-enhanced)](https://pepy.tech/project/android-sdk-enhanced) [![PyPI version](https://badge.fury.io/py/android-sdk-enhanced.svg)](https://badge.fury.io/py/android-sdk-enhanced) [![CircleCI](https://circleci.com/gh/ashishb/android-sdk-enhanced/tree/master.svg?style=shield&circle-token=b64e11ee679a0856cf50dbe559e3e59ebbb26466)](https://circleci.com/gh/ashishb/android-sdk-enhanced/tree/master) [![Build Status](https://travis-ci.org/ashishb/android-sdk-enhanced.svg)](https://travis-ci.org/ashishb/android-sdk-enhanced) ![Python 3.6](https://img.shields.io/badge/python-3.6-brightgreen.svg)

A better version of the command-line android SDK and AVD manager tools with a more intuitive interface

### Installation

`pip3 install android-sdk-enhanced`

Note: Python 2 install is not supported

A better version of the command-line android tool with a more intuitive command-line interface.

### Usage

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

### Options
    -v, --verbose       Verbose mode


### Sub-command description
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