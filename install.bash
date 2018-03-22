#!/usr/bin/env bash

BASE_URL = "https://github.com/radtomas/sufler/archive/initial-version.zip"

if [ -z "$install_dir" ]; then
    install_dir="."
else
    if [ "${install_dir:0:1}" == "~" ]; then
        install_dir="${HOME}${install_dir:1}"
    fi
    if [ "${install_dir: -1}" == "/" ]; then
        install_dir="${install_dir:0:${#install_dir}-1}"
    fi
fi

curl -fsSL $BASE_URL -o sufler.zip
if [ ! -f sufler.zip ]; then
    printf "\n\e[1;31mInstallation unsuccessful due to failed download\e[0m\n"
    exit
fi
unzip -o sufler.zip -d "$install_dir"
rm -f sufler.zip
if [ ! -d "$install_dir/.sufler" ]; then
    printf "\n\e[1;31mSufler installation unsuccessful due to failed unzip\e[0m\n"
    exit
fi
pip install -e "$install_dir/.sufler/"

printf "\n\e[1;32mInstallation completed\e[0m\n"