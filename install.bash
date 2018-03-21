#!/usr/bin/env bash

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

curl -fsSL https://github.com/radtomas/sufler/archive/initial-version.zip -o sufler.zip
if [ ! -f sufler.zip ]; then
    printf "\n\e[1;31mInstallation unsuccessful due to failed download\e[0m\n"
    exit
fi
unzip -o sufler.zip -d "$install_dir"
rm -f sufler.zip
if [ ! -d "$install_dir/sufler-master" ]; then
    printf "\n\e[1;31mSufler installation unsuccessful due to failed unzip\e[0m\n"
    exit
fi
pip install -e "$install_dir/sufler-master/"

curl -fsSL https://github.com/radtomas/sufler-completions/archive/initial-version.zip -o sufler-completions.zip
if [ ! -f sufler.zip ]; then
    printf "\n\e[1;31mCompletions installation unsuccessful due to failed download\e[0m\n"
    exit
fi
unzip -o sufler-completions.zip -d "$install_dir/completions/"
rm -f sufler.zip
if [ ! -d "$install_dir/sufler-master" ]; then
    printf "\n\e[1;31mCompletions installation unsuccessful due to failed unzip\e[0m\n"
    exit
fi

printf "\n\e[1;33mAuto-completion requires sudo\e[0m\n"
if [ "$USER" == 'root' ]; then
    if [ -z "$shell" ]; then
        sudo python 'sufler-master/sufler/cli.py' 'install'
    fi
else
    printf "\n\e[1;33mNeeds sudo - use 'sudo sufler install'\e[0m\n"
fi
printf "\n\e[1;32mInstallation completed\e[0m\n"