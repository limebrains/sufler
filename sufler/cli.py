import os
import shutil
import subprocess
import zipfile

import click
import requests
import yaml

from sufler.base import SUFLER_BASE_PATH

cli = click.Group()

PATH_FOR_SHELL = {
    'bash': [
        '/usr/local/etc/bash_completion.d/',
        '/usr/bin/bash_completion.d/'
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
            '(python \"{1}/backends/fish/fish.py\" (commandline -cp))\' -f',
}

CONFIG_DATA = {
    'repos': [
        {
            'url': 'https://github.com/limebrains/sufler-completions.git',
        },
        {
            'url': 'git@github.com:limebrains/sufler-completions.git',
        },
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
        possible_locations = PATH_FOR_SHELL[self.shell_name]
        for location in possible_locations:
            if os.path.exists(location):
                return location

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
        with open(str(self.install_file_path), 'r') as f:
            completer_content = f.read()

        for command in commands_not_installed(commands, completer_content):
            completer_content += COMMAND_FOR_SHELL[
                self.shell_name
            ].format(command)

        with open(str(self.install_file_path), 'w') as f:
            f.write(completer_content)


class Bash(BashZshInstallCommandsMixin, BaseShell):
    shell_name = 'bash'

    def initialize(self):
        with open(SUFLER_BASE_PATH + '/backends/bash/completer', 'r') as f:
            completer_content = f.read()

        completer_content = completer_content.format(
            python_script_path='{0}/backends/'
                               'bash/bash.py'.format(SUFLER_BASE_PATH)
        )

        with open(str(self.install_file_path), 'w') as f:
            f.write(completer_content)

    def install(self, commands):
        if not os.path.exists(self.install_file_path):
            self.initialize()
        self.install_commands(commands)

        try:
            subprocess.check_output(
                '. {0}completer'.format(self.install_path)
            )
        except OSError:
            pass


class Zsh(BashZshInstallCommandsMixin, BaseShell):
    shell_name = 'zsh'

    def initialize(self):
        command = 'cp {0}/backends/zsh/completer {1}'.format(
            SUFLER_BASE_PATH,
            self.install_path
        )
        subprocess.check_output(command, shell=True)

        with open(str(self.install_file_path), 'r') as f:
            completer_content = f.read()

        bash_backend_path = "{0}/backends/bash".format(SUFLER_BASE_PATH)

        with open(str(bash_backend_path + '/completer'), 'r') as f:
            bash_completer_content = f.read()

        completer_content = completer_content.format(
            bash_content=bash_completer_content.format(
                python_script_path=bash_backend_path + '/bash.py'
            )
        )

        with open(str(self.install_file_path), 'w') as f:
            f.write(completer_content)

        command = 'echo ". {0}" >> ~/.zshrc'.format(
            self.install_path + '/completer'
        )
        subprocess.check_output(command, shell=True)

    def install(self, commands):
        if not os.path.exists(self.install_file_path):
            self.initialize()
        self.install_commands(commands)


class Fish(BaseShell):
    shell_name = 'fish'

    def install(self, commands):
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
            command_completer_file = '{0}/{1}.fish'.format(
                self.install_path,
                command
            )

            with open(command_completer_file, 'w') as f:
                f.write(COMMAND_FOR_SHELL[self.shell_name].format(
                    command,
                    SUFLER_BASE_PATH
                ))


class PowerShell(BaseShell):
    shell_name = 'powershell'

    @property
    def install_file_path(self):
        return '{0}Microsoft.PowerShell_profile.ps1'.format(
            self.install_path
        )

    def install(self, commands):
        if not os.path.exists(self.install_file_path):

            completer_file = '{0}/backends/powershell/completer'.format(
                SUFLER_BASE_PATH
            )

            with open(completer_file, 'r') as f:
                completer_content = f.read()

            completer_content = completer_content.format(
                python_script_path="{0}/backends/powershell/"
                                   "powershell.py".format(SUFLER_BASE_PATH))

            completer_script_path = "{0}/backends/powershell/" \
                                    "completer.ps1".format(SUFLER_BASE_PATH)

            with open(str(completer_script_path), 'w') as f:
                f.write(completer_content)

            autoloader_path = '{0}/.config/powershell'.format(
                os.path.expanduser('~')
            )
            if not os.path.exists(autoloader_path):
                command = 'mkdir {0}'.format(autoloader_path)
                subprocess.check_output(command, shell=True)

            command = 'echo ". {0}" >> {1}'.format(
                completer_script_path,
                str(self.install_file_path)
            )
            subprocess.check_output(command, shell=True)


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
    for shell_name, shell_cls in SHELL_NAME_TO_CLASS.items():
        shell = shell_cls()
        if shell.exists():
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


def get_commands():
    """ Looking for commands .yml file in completions directory

    :return: List of commands found in completions directory
    """
    completions_path = os.path.expanduser('~/.sufler/completions/')
    completions_path_files = [
        file
        for file in os.listdir(completions_path)
        if file.endswith('.yml')
    ]

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

        if urls['url'].endswith('.zip'):
            result = requests.get(urls['url'])

            with open(zip_file_path, 'wb') as out_zip_file:
                out_zip_file.write(result.content)

            with zipfile.ZipFile(zip_file_path) as zip_file:
                zip_file.extractall(path=zip_dir_path)

            os.remove(zip_file_path)


def install_completion_files():
    """
    Check difference between sufler completions folder
    and git completions folder.
    After check copy only files not in sufler completions folder.
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

    for file in completions_not_installed:
        shutil.copyfile(
            '{0}/{1}'.format(zip_completions_path, file),
            os.path.expanduser('~/.sufler/completions/' + file)
        )


@cli.command('install')
@click.option(
    '--name',
    '-n',
    default=None,
    help='install specified completion')
@click.pass_context
def install_command(ctx, name):
    """install completions"""

    ctx.invoke(init_command)

    install_completion_files()

    shells = detect_shells()
    commands = get_commands()
    for shell in shells:
        shell.install(commands)


@cli.command('init')
def init_command():
    """initialize Sufler directory and config file"""

    sufler_dir = os.path.expanduser('~') + '/.sufler'
    if not os.path.exists(sufler_dir):
        os.mkdir(sufler_dir)

    config_file_path = sufler_dir + '/.config'
    if not os.path.exists(config_file_path):
        with open(config_file_path, 'w') as outfile:
            yaml.dump(CONFIG_DATA, outfile, default_flow_style=False)

    if not os.path.exists(sufler_dir + '/completions'):
        os.mkdir(sufler_dir + '/completions')


@cli.command('run')
@click.argument('command')
def run_command(command):
    """run command from <Run >"""
    subprocess.Popen(command.split(' ')[1:])


def main():
    cli()


if __name__ == '__main__':
    main()
