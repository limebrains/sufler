#!/usr/bin/env bash

base_url = "https://github.com/limebrains/sufler/archive/master.zip"

if [ -z "$install_dir" ]; then
    install_dir="${HOME}"
else
    if [ "${install_dir:0:1}" == "~" ]; then
        install_dir="${HOME}${install_dir:1}"
    fi
    if [ "${install_dir: -1}" == "/" ]; then
        install_dir="${install_dir:0:${#install_dir}-1}"
    fi
fi

curl -fsSL $base_url -o sufler.zip
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
sudo pip install -e "$install_dir/.sufler/sufler-master/"
sufler install

printf "\n\e[1;32mInstallation completed\e[0m\n"