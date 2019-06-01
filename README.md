# Android Tool [![Downloads](https://pepy.tech/badge/androidtool)](https://pepy.tech/project/androidtool) [![PyPI version](https://badge.fury.io/py/androidtool.svg)](https://badge.fury.io/py/androidtool) ![Python 3.6](https://img.shields.io/badge/python-3.6-brightgreen.svg) [![Build Status](https://img.shields.io/travis/ashishb/androidtool/master.svg?label=Travis%20CI)](https://travis-ci.org/ashishb/androidtool) [![CircleCI](https://img.shields.io/circleci/project/github/ashishb/androidtool.svg?label=Circle%20CI)](https://circleci.com/gh/ashishb/androidtool)

A better version of the command-line android SDK and AVD manager tools with a more intuitive interface

### Installation

`pip3 install androidtool`

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


### Usage example

```
$ androidtool doctor
Checking java version...
Correct Java version 1.8 is installed
Checking SDK manager is installed...
Checking that basic Android packages are installed...
Package 1/8: "build-tools;28.0.3" is installed
Package 2/8: "emulator" is installed
Package 3/8: "tools" is installed
Package 4/8: "platform-tools" is installed
Package 5/8: "extras;android;m2repository" is installed
Package 6/8: "extras;google;m2repository" is installed
Package 7/8: "patcher;v4" is installed
Package 8/8: "extras;intel;Hardware_Accelerated_Execution_Manager" is installed
```

```
$ androidtool list build tools
...
build-tools;26.0.1
build-tools;26.0.2
build-tools;26.0.3
build-tools;27.0.0
build-tools;27.0.1
build-tools;27.0.2
build-tools;27.0.3
build-tools;28.0.0
build-tools;28.0.0-rc1
build-tools;28.0.0-rc2
build-tools;28.0.1
build-tools;28.0.2
build-tools;28.0.3
```

```
$ androidtool list api versions --arm
Google API type: default (Standard Android image; no Google API)
armeabi-v7a -> 14, 14, 10, 14, 15, 16, 17, 18, 19, 21, 22, 24

Google API type: google_apis
armeabi-v7a -> 10, 15, 17, 18, 19, 21, 22, 23, 24, 25

Google API type: android-tv
armeabi-v7a -> 21, 23

Google API type: android-wear
armeabi-v7a -> 23, 25

Google API type: android-wear-cn
armeabi-v7a -> 25
```

```
$ androidtool list api versions --x86 --google-apis
Google API type: google_apis
x86 -> 10, 15, 16, 17, 18, 19, 21, 22, 23, 24, 25, 26, 27, 28
x86_64 -> 21, 22, 23, 24, 25, 26, 28
```

```
$ androidtool list avds
Available Android Virtual Devices:
Name: test_avd1
Path: /usr/local/Cellar/android-sdk/.android/avd/test_avd1.avd
Target: Default Android System Image
Based on: Android API 28 Tag/ABI: default/x86
---------
Name: test_avd2
Path: /usr/local/Cellar/android-sdk/.android/avd/test_avd2.avd
Target: Default Android System Image
Based on: Android API 28 Tag/ABI: default/x86
```

```
$ androidtool update all
No packages to update
All licenses accepted
```
