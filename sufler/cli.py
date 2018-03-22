import os

import yaml
import click
import pathlib
import subprocess

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
    'fish': '\ncomplete --command {0} --arguments \'(python \"{1}/backends/fish/fish.py\" (commandline -cp))\' -f',
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

        :param commands: List of commands founded in completions directory
        :return: None
        """
        pass

    def install(self, commands):
        """ Install completion file for shell

        :param commands: List of commands founded in completions directory
        :return: None
        """
        pass

    def get_install_path(self):
        """ Check that install directory from PATH_FOR_SHELL exists and return him

        :return: Install path
        """
        possible_locations = PATH_FOR_SHELL[self.shell_name]
        for location in possible_locations:
            install_path = pathlib.Path(location)
            if install_path.exists():
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
        return pathlib.Path(self.install_path + '/completer')

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
            completer_content += COMMAND_FOR_SHELL[self.shell_name].format(command)

        with open(str(self.install_file_path), 'w') as f:
            f.write(completer_content)


class Bash(BashZshInstallCommandsMixin, BaseShell):
    shell_name = 'bash'

    def initialize(self):
        with open(SUFLER_BASE_PATH + '/backends/bash/completer', 'r') as f:
            completer_content = f.read()

        completer_content = completer_content.format(
            python_script_path='{0}/backends/bash/bash.py'.format(SUFLER_BASE_PATH)
        )

        with open(str(self.install_file_path), 'w') as f:
            f.write(completer_content)

    def install(self, commands):
        install_file_path = pathlib.Path(self.install_path + '/completer')
        if not install_file_path.exists():
            self.initialize()
        self.install_commands(commands)


class Zsh(BashZshInstallCommandsMixin, BaseShell):
    shell_name = 'zsh'

    def initialize(self):
        command = 'cp {0}/backends/zsh/completer {1}'.format(SUFLER_BASE_PATH, self.install_path)
        subprocess.check_output(command, shell=True)

        with open(str(self.install_file_path), 'r') as f:
            completer_content = f.read()

        bash_backend_path = "{0}/backends/bash".format(SUFLER_BASE_PATH)

        with open(str(bash_backend_path + '/completer'), 'r') as f:
            bash_completer_content = f.read()

        completer_content = completer_content.format(
            bash_content=bash_completer_content.format(python_script_path=bash_backend_path + '/bash.py')
        )

        with open(str(self.install_file_path), 'w') as f:
            f.write(completer_content)

        command = 'echo ". {0}" >> ~/.zshrc'.format(self.install_path + '/completer')
        subprocess.check_output(command, shell=True)

    def install(self, commands):
        install_file_path = pathlib.Path(self.install_path + '/completer')
        if not install_file_path.exists():
            self.initialize()
        self.install_commands(commands)


class Fish(BaseShell):
    shell_name = 'fish'

    def install(self, commands):
        current_installed_commands = ' '.join(
            str(file)
            for file in pathlib.Path(self.install_path).glob('*.fish')
        )

        for command in commands_not_installed(commands, current_installed_commands):
            with open('{0}/{1}.fish'.format(self.install_path, command), 'w') as f:
                f.write(COMMAND_FOR_SHELL[self.shell_name].format(command, SUFLER_BASE_PATH))


class PowerShell(BaseShell):
    shell_name = 'powershell'

    @property
    def install_file_path(self):
        return pathlib.Path(self.install_path + '/Microsoft.PowerShell_profile.ps1')

    def install(self, commands):
        if not self.install_file_path.exists():
            with open('{0}/backends/powershell/completer'.format(SUFLER_BASE_PATH), 'r') as f:
                completer_content = f.read()

            completer_content = completer_content.format(
                python_script_path="{0}/backends/powershell/powershell.py".format(SUFLER_BASE_PATH))

            completer_script_path = '{0}/backends/powershell/completer.ps1'.format(SUFLER_BASE_PATH)

            with open(str(completer_script_path), 'w') as f:
                f.write(completer_content)

            autoloader_path = pathlib.Path('{0}/.config/powershell'.format(os.path.expanduser('~')))
            if not autoloader_path.exists():
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

    :param commands: List of commands founded in completions directory
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

    :return: List of commands founded in completions directory
    """
    completions_path = pathlib.Path(str(pathlib.Path.cwd()))
    return [
        str(command).split('/')[-1][:-4]
        for command in completions_path.glob('completions/*.yml')
    ]


# def get_completions_directory_from_git(repos):
#


@cli.command('install')
@click.option('--name', '-n', default=None, help='install specified completion')
@click.pass_context
def install_completions(ctx, name):
    """install completions"""
    #
    # if not pathlib.Path(pathlib.Path().home()/'.sufler').exists():
    #     result = ctx.invoke(init_command, content=ctx.forward(add_name))
    #     init_command()

    if name:
        pass

    shells = detect_shells()
    commands = get_commands()
    for shell in shells:
        shell.install(commands)


@cli.command('init')
def init_command():
    """initialize Sufler directory and config file"""

    sufler_dir = pathlib.Path().home()/'.sufler'
    if not sufler_dir.exists():
        os.mkdir(sufler_dir, 775)
        print('Sufler config directory created')

    config_file_path = sufler_dir/'.config'
    if not config_file_path.exists():
        config_data = {
            'repos': [
                {
                    'url': 'https://github.com/limebrains/sufler-completions.git',
                },
                {
                    'url': 'git@github.com:limebrains/sufler-completions.git',
                },
                {
                    'https://github.com/limebrains/sufler-completions/archive/master.zip'
                }
            ]
        }

        with open(config_file_path, 'w') as outfile:
            yaml.dump(config_data, outfile, default_flow_style=False)

        print('Created Sufler config file')

    if not pathlib.Path(sufler_dir/'completions').exists():
        os.mkdir(sufler_dir/'completions')
        print('Create completions dictionary')


@cli.command('run')
@click.argument('command')
def run_command(command):
    """run command from <Run >"""
    subprocess.Popen(command.split(' ')[1:])


def main():
    cli()


if __name__ == '__main__':
    main()
