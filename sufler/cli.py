import logging
import os
import shutil
import subprocess
import sys
import zipfile

import click
import click_log
import requests
import yaml
from six.moves import input
from sufler.base import SUFLER_BASE_PATH

logger = logging.getLogger(__name__)
click_log.basic_config(logger)

cli = click.Group()

PATH_FOR_SHELL = {
    'bash': [
        '/usr/local/etc/bash_completion.d/',
        '/usr/bin/bash_completion.d/',
        '/etc/bash_completion.d/',
    ],
    'fish': [
        '{0}/.config/fish/completions/'.format(os.path.expanduser('~')),
    ],
    'zsh': [
        '/usr/local/share/zsh-completions/',
    ],
    'powershell': [
        '{0}/.config/powershell/'.format(os.path.expanduser('~')),
    ],
}

COMMAND_FOR_SHELL = {
    'bash': '\ncomplete -F _completer -o default {0}',
    'zsh': '\ncomplete -F _completer -o default {0}',
    'fish': '\ncomplete --command {0} --arguments \''
            '({1} \"{2}/backends/fish/fish.py\" (commandline -cp))\' -f',
}

CONFIG_DATA = {
    'repos': [
        {
            'url': 'https://github.com/limebrains/sufler-completions'
                   '/archive/master.zip'
        },
    ]
}


class BaseShell(object):
    """ Template class of shells for install

    """

    def initialize(self):
        """ Rewrite completer template to install_path directory

        :return: None
        """
        pass

    def install_commands(self, commands):
        """ Add commands to completer file for shell

        :param commands: List of commands found in completions directory
        :return: None
        """
        pass

    def install(self, commands):
        """ Install completion file for shell

        :param commands: List of commands found in completions directory
        :return: None
        """
        pass

    def get_install_path(self):
        """ Check that install directory from PATH_FOR_SHELL exists and return him

        :return: Install path
        """
        logger.debug("Looking for " + self.shell_name)
        possible_locations = PATH_FOR_SHELL[self.shell_name]
        for location in possible_locations:
            if os.path.exists(location):
                return location

        logger.debug("Shell not found")
        user_path = str(
            input(
                'Path to shell completions directory not found. '
                'Please enter own path to {0} completions:\n'.format(
                    self.shell_name
                )
            )
        )

        if user_path:
            logger.debug("Append path " + user_path)
            PATH_FOR_SHELL[self.shell_name].append(user_path)

        logger.debug("User path " + user_path)
        return user_path

    @property
    def install_path(self):
        """ Directory path which contains completers for current shell

        :return: Install path
        """
        return self.get_install_path()

    @property
    def install_file_path(self):
        """ Path where completer file will be installed

        :return: Install file path
        """
        return '{0}completer'.format(self.install_path)

    def exists(self):
        """ Check shell path exists

        :return: True if exists False if not
        """
        return bool(self.get_install_path())


class BashZshInstallCommandsMixin:
    def install_commands(self, commands):
        logger.debug("Install commands for " + self.shell_name)
        logger.debug("Read completer content")
        with open(self.install_file_path, 'r') as f:
            completer_content = f.read()

        logger.debug("Append commands")
        for command in commands_not_installed(commands, completer_content):
            completer_content += COMMAND_FOR_SHELL[
                self.shell_name
            ].format(command)

        logger.debug("Write completer " + self.install_file_path)
        with open(self.install_file_path, 'w') as f:
            f.write(completer_content)


class Bash(BashZshInstallCommandsMixin, BaseShell):
    shell_name = 'bash'

    def initialize(self):
        logger.debug("Install bash")
        logger.debug("Read completer content")
        with open(SUFLER_BASE_PATH + '/backends/bash/completer', 'r') as f:
            completer_content = f.read()

        completer_content = completer_content.format(
            python_executable=sys.executable,
            python_script_path='{0}/backends'
                               '/bash/bash.py'.format(SUFLER_BASE_PATH)
        )

        logger.debug("Write completer content" + self.install_file_path)
        with open(str(self.install_file_path), 'w') as f:
            f.write(completer_content)
        logger.debug("Install bash end")

    def install(self, commands):
        if not os.path.exists(self.install_file_path):
            self.initialize()

        self.install_commands(commands)


class Zsh(BashZshInstallCommandsMixin, BaseShell):
    shell_name = 'zsh'

    def initialize(self):
        logger.debug("Initialize zsh")
        command = 'cp {0}/backends/zsh/completer {1}'.format(
            SUFLER_BASE_PATH,
            self.install_path
        )
        subprocess.check_output(command, shell=True)

        logger.debug("Get completer content")
        with open(str(self.install_file_path), 'r') as f:
            completer_content = f.read()

        bash_backend_path = "{0}/backends/bash".format(SUFLER_BASE_PATH)

        logger.debug("Append zsh commands")
        with open(str(bash_backend_path + '/completer'), 'r') as f:
            bash_completer_content = f.read()

        completer_content = completer_content.format(
            bash_content=bash_completer_content.format(
                python_executable=sys.executable,
                python_script_path=bash_backend_path + '/bash.py'
            )
        )

        logger.debug(
            "Write completer content to file " + self.install_file_path
        )
        with open(str(self.install_file_path), 'w') as f:
            f.write(completer_content)

        logger.debug(
            "Add completer path to startup script " + self.install_file_path
        )
        command = 'echo ". {0}" >> ~/.zshrc'.format(
            self.install_path + 'completer'
        )
        if os.path.isfile(os.path.expanduser('~/.zshrc')):
            index = command.find('"') + 1
            command = '{0} && {1}'.format(command[:index], command[index:])

        subprocess.check_output(command, shell=True)

        logger.debug("Zsh install end")

    def install(self, commands):
        if not os.path.exists(self.install_file_path):
            self.initialize()

        self.install_commands(commands)


class Fish(BaseShell):
    shell_name = 'fish'

    def install(self, commands):
        logger.debug("Install fish")
        current_installed_commands = [
            file
            for file in os.listdir(self.install_path)
            if file.endswith('.fish')
        ]

        not_installed_commands = commands_not_installed(
                commands,
                current_installed_commands
        )

        for command in not_installed_commands:
            logger.debug("Create fish script for " + command)
            command_completer_file = '{0}{1}.fish'.format(
                self.install_path,
                command
            )

            logger.debug("Write script file in " + command_completer_file)
            with open(command_completer_file, 'w') as f:
                f.write(COMMAND_FOR_SHELL[self.shell_name].format(
                    command,
                    sys.executable,
                    SUFLER_BASE_PATH
                ))
        logger.debug("Fish install end")


class PowerShell(BaseShell):
    shell_name = 'powershell'

    @property
    def install_file_path(self):
        return '{0}Microsoft.PowerShell_profile.ps1'.format(
            self.install_path
        )

    def install(self, commands):
        logger.debug("Install powershell")

        completer_script_path = "{0}/backends/powershell/" \
                                "completer.ps1".format(SUFLER_BASE_PATH)

        if not os.path.exists(self.install_file_path):
            logger.debug("Add completer to powershell startup")

            autoloader_path = '{0}/.config/powershell'.format(
                os.path.expanduser('~')
            )
            if not os.path.exists(autoloader_path):
                logger.debug(
                    "Make folder for startup script " + autoloader_path
                )
                command = 'mkdir {0}'.format(autoloader_path)
                subprocess.check_output(command, shell=True)

            command = 'echo ". {0}" >> {1}'.format(
                completer_script_path,
                str(self.install_file_path)
            )
            subprocess.check_output(command, shell=True)

        completer_file = '{0}/backends/powershell/completer'.format(
            SUFLER_BASE_PATH
        )

        logger.debug("Powershell completer install start")

        with open(completer_file, 'r') as f:
            completer_content = f.read()

        completer_content = completer_content.format(
            python_executable=sys.executable,
            python_script_path="{0}/backends/powershell/"
                               "powershell.py".format(SUFLER_BASE_PATH)
        )

        logger.debug("Write completer content: " + completer_script_path)
        with open(completer_script_path, 'w') as f:
            f.write(completer_content)

        logger.debug("Powershell completer install end")


SHELL_NAME_TO_CLASS = {
    'bash': Bash,
    'zsh': Zsh,
    'fish': Fish,
    'powershell': PowerShell,
}


def detect_shells():
    """ Checking which one shell listed in PATH_FOR_SHELL are installed

    :return: Detected shells
    """
    shells = []

    logger.debug("Detect shells")
    for shell_name, shell_cls in SHELL_NAME_TO_CLASS.items():
        logger.debug("Looking for " + shell_name)
        shell = shell_cls()
        if shell.exists():
            logger.debug("Detected " + shell_name)
            shells.append(shell)
    return shells


def commands_not_installed(commands, completer_content):
    """ Checking for installed commands in exists completer file

    :param commands: List of commands found in completions directory
    :param completer_content: Content of current installed complete file
    :return: List of not installed commands
    """
    return [
        command
        for command in commands
        if command not in completer_content
    ]


def get_commands(name):
    """ Looking for commands .yml file in completions directory

    :return: List of commands found in completions directory
    """
    completions_path = os.path.expanduser('~/.sufler/completions/')
    completions_path_files = [
        file
        for file in os.listdir(completions_path)
        if file.endswith('.yml')
    ]

    logger.debug(
        "Completion files from sufler home " +
        ', '.join(completions_path_files)
    )

    if name and os.path.isfile('{0}{1}.yml'.format(completions_path, name)):
        return [name]

    return [
        str(command).split('/')[-1][:-4]
        for command in completions_path_files
    ]


def get_completions_directory_from_git():
    """Download zip file from git and extrack to dir"""
    for urls in CONFIG_DATA['repos']:
        zip_file_path = '{0}/.sufler/zip_completions.zip'.format(
            os.path.expanduser('~')
        )
        zip_dir_path = '{0}/.sufler/zip_completions/'.format(
            os.path.expanduser('~')
        )
        logger.debug("Download zip file")
        if urls['url'].endswith('.zip'):
            result = requests.get(urls['url'])

            with open(zip_file_path, 'wb') as out_zip_file:
                out_zip_file.write(result.content)

            logger.debug("Save zip file")

            with zipfile.ZipFile(zip_file_path) as zip_file:
                zip_file.extractall(path=zip_dir_path)

            logger.debug("Extract zip file")

            os.remove(zip_file_path)


def install_completion_files():
    """
    Check difference between sufler completions folder
    and git completions folder.
    After check copy only files not in sufler completions folder.

    :param name: completion fle name
    """
    get_completions_directory_from_git()

    sufler_completions_files = os.listdir(
        os.path.expanduser('~/.sufler/completions')
    )
    zip_completions_path = os.path.expanduser(
        '~/.sufler/zip_completions/sufler-completions-master/completions'
    )
    zip_completions_files = os.listdir(zip_completions_path)

    completions_not_installed = set(zip_completions_files).difference(
        sufler_completions_files
    )

    logger.debug("Copy files")
    for file in completions_not_installed:
        logger.debug("Install completion file " + file)
        shutil.copyfile(
            '{0}/{1}'.format(zip_completions_path, file),
            os.path.expanduser('~/.sufler/completions/' + file)
        )
    shutil.rmtree(os.path.expanduser('~/.sufler/zip_completions'))


@cli.command('install')
@click.option(
    '--name',
    '-n',
    default=None,
    help='install specified completion')
@click.pass_context
@click_log.simple_verbosity_option(logger)
def install_command(ctx, name):
    """install completions"""

    ctx.invoke(init_command)

    install_completion_files()

    shells = detect_shells()

    commands = get_commands(name)

    for shell in shells:
        shell.install(commands)


@cli.command('init')
@click_log.simple_verbosity_option(logger)
def init_command():
    """initialize Sufler directory and config file"""

    logger.debug("Init command")

    sufler_dir = os.path.expanduser('~') + '/.sufler'
    if not os.path.exists(sufler_dir):
        logger.debug("Make sufler home directory")
        os.mkdir(sufler_dir)

    config_file_path = sufler_dir + '/.config'
    if not os.path.exists(config_file_path):
        logger.debug("Write config to sufler config file")
        with open(config_file_path, 'w') as outfile:
            yaml.dump(CONFIG_DATA, outfile, default_flow_style=False)

    if not os.path.exists(sufler_dir + '/completions'):
        logger.debug("Make sufler completions directory")
        os.mkdir(sufler_dir + '/completions')


@cli.command('run')
@click.argument('command')
@click_log.simple_verbosity_option(logger)
def run_command(command):
    """run command from <Run >"""
    logger.debug("Run command for " + command)
    subprocess.Popen(command.split(' ')[1:])


def main():
    cli()


if __name__ == '__main__':
    main()
