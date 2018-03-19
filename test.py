import base
import cli
import backends

import pytest
from click import testing
from mock import patch, mock_open


# Test base.py
@pytest.mark.parametrize('file, expected_value', [
    ('base.py', ['base.py']),
    ('docs/', ['docs/index.rst',
               'docs/.DS_Store',
               'docs/_templates/',
               'docs/Makefile',
               'docs/conf.py',
               'docs/_static/',
               'docs/user/',
               'docs/make.bat',
               'docs/_build/',
               'docs/modules/'
               ]),
])
def test_get_files_autocomplete(file, expected_value):
    assert base.get_files_autocomplete(file) == expected_value


@pytest.mark.parametrize('command', [
    'food',
    'cargo',
])
def test_autocomplete_file_for_command(command):
    autocomplete_dict = base.get_autocomplete_file_for_command(command)
    assert isinstance(list(autocomplete_dict)[0], dict)


@pytest.mark.parametrize('key, arguments, expected_value', [
    ('<Run> TREE~1 TREE~2', ['fruit', 'README.md', 'cat'], '<Run> cat README.md'),
    ('', ['food', 'other'], ''),
    ('TREE~1 TREE~2', ['food', 'grape', 'cos'], 'cos grape')
])
def test_replace_tree_marks(key, arguments, expected_value):
    assert base.replace_tree_marks(key, arguments) == expected_value


@pytest.mark.parametrize('command_name, all_arguments, expected_value', [
    ('food', ['path', '3', 'food', 'veg', '-c'], ['broccoli', '"brussel sprouts"', 'asparagus']),
    ('food', ['path', '3', 'food', 'fruit', 'README.md', 'cat'], []),
    ('food', ['path', '3', 'food', '-r', 'README.md'], ['fruit', 'veg', 'candy', 'booze:', 'meat', 'dairy:', '-f', '-r', '--color', 'other', 'deploy']),
    ('food', ['path', '3', 'food', '--color', 'black'], ['avocado', 'tomato']),
])
def test_completion(command_name, all_arguments, expected_value):
    assert list(base.completion(command_name, all_arguments).keys()) == expected_value


# Test cli.py
def test_detect_shells():
    for shell in cli.detect_shells():
        assert isinstance(type(shell), type(cli.BaseShell))


@pytest.mark.parametrize('commands, completer_content, expected_values', [
    (['food', 'cargo'], 'Lorem food ipsum cargo', []),
    (['test', 'cargo'], 'Lorem test ipsum cos', ['cargo'])
])
def test_commands_not_installed(commands, completer_content, expected_values):
    assert cli.commands_not_installed(commands, completer_content) == expected_values


def test_get_commands():
    assert cli.get_commands() == ['food', 'cargo', 'flake8']


@patch('cli.detect_shells', return_value=[
    cli.Bash(),
    cli.Fish(),
    cli.Zsh(),
    cli.PowerShell(),
])
@patch('cli.get_commands', return_values=[
    'cargo',
    'food',
    'flake8',
])
@patch('cli.BaseShell.install')
def test_install_completions(mock_install, mock_get_commands, mock_detect_shells):
    result = testing.CliRunner().invoke(cli.install_completions)

    assert result.exit_code == 0
    assert len(mock_get_commands.mock_calls) == 4
    mock_detect_shells.assert_called


@pytest.mark.parametrize('command', [
    ['run ls'],
    ['run echo "cos"']
])
def test_run_command(command):
    result = testing.CliRunner().invoke(cli.run_command, command)
    assert result.exit_code == 0


@pytest.mark.parametrize('shell_to_class, expected_values', [
    (cli.SHELL_NAME_TO_CLASS['bash'], cli.PATH_FOR_SHELL['bash']),
    (cli.SHELL_NAME_TO_CLASS['fish'], cli.PATH_FOR_SHELL['fish']),
    (cli.SHELL_NAME_TO_CLASS['zsh'], cli.PATH_FOR_SHELL['zsh']),
    (cli.SHELL_NAME_TO_CLASS['powershell'], cli.PATH_FOR_SHELL['powershell']),
])
def test_base_shell_get_install_path(shell_to_class, expected_values):
    shell = shell_to_class()
    assert shell.get_install_path() == expected_values[0]


@pytest.mark.parametrize('shell_to_class, expected_values', [
    (cli.SHELL_NAME_TO_CLASS['bash'], cli.PATH_FOR_SHELL['bash']),
    (cli.SHELL_NAME_TO_CLASS['fish'], cli.PATH_FOR_SHELL['fish']),
    (cli.SHELL_NAME_TO_CLASS['zsh'], cli.PATH_FOR_SHELL['zsh']),
    (cli.SHELL_NAME_TO_CLASS['powershell'], cli.PATH_FOR_SHELL['powershell']),
])
def test_base_shell_install_path(shell_to_class, expected_values):
    shell = shell_to_class()
    assert shell.install_path == expected_values[0]


@pytest.mark.parametrize('shell_to_class, expected_values', [
    (cli.SHELL_NAME_TO_CLASS['bash'], cli.PATH_FOR_SHELL['bash']),
    (cli.SHELL_NAME_TO_CLASS['fish'], cli.PATH_FOR_SHELL['fish']),
    (cli.SHELL_NAME_TO_CLASS['zsh'], cli.PATH_FOR_SHELL['zsh']),
])
def test_base_shell_install_file_path(shell_to_class, expected_values):
    shell = shell_to_class()
    assert str(shell.install_file_path) == '{0}completer'.format(expected_values[0])


@pytest.mark.parametrize('shell_to_class', [
    (cli.SHELL_NAME_TO_CLASS['bash']),
    (cli.SHELL_NAME_TO_CLASS['fish']),
    (cli.SHELL_NAME_TO_CLASS['zsh']),
    (cli.SHELL_NAME_TO_CLASS['powershell']),
])
def test_base_shell_exists(shell_to_class):
    shell = shell_to_class()
    assert shell.exists()


@pytest.mark.parametrize('shell_to_cls', [
    (cli.SHELL_NAME_TO_CLASS['bash']),
    (cli.SHELL_NAME_TO_CLASS['zsh']),
])
def test_bash_zsh_install_commands(shell_to_cls):
    shell = shell_to_cls()
    commands = ['food', 'cargo', 'flake8']

    m = mock_open(read_data='bash_completer cargo food ')
    with patch('cli.open', m):
        shell.install_commands(commands)

    assert 'bash_completer cargo food \\ncomplete -F _completer -o default flake8' in str(m.mock_calls[6])


def test_bash_shell_initialize():
    shell = cli.Bash()

    m = mock_open(read_data='bash_completer {python_script_path}')
    with patch('cli.open', m):
        shell.initialize()

    assert 'bash_completer /Users/radtomas/PycharmProjects/sufler/backends/bash/bash.py' in str(m.mock_calls[6])


@patch('cli.Bash.exists', return_value=False)
@patch('cli.Bash.initialize', side_effect=True)
@patch('cli.Bash.install_commands', return_value=True)
def test_bash_install(mock_install_commands, mock_initialize, mock_exists):
    shell = cli.Bash()
    commands = ['food', 'cargo', 'flake8']

    shell.install(commands)

    assert mock_initialize
    assert mock_install_commands


@patch('cli.subprocess.check_output')
def test_zsh_initialize(mock_check_output):
    shell = cli.Zsh()

    m = mock_open(read_data='bash_completer')

    with patch('cli.open', m):
        shell.initialize()

    assert 'bash_completer' in str(m.mock_calls[10])


@patch('cli.Zsh.exists', return_value=False)
@patch('cli.Zsh.initialize', side_effect=True)
@patch('cli.Zsh.install_commands', return_value=True)
def test_zsh_install(mock_install_commands, mock_initialize, mock_exists):
    shell = cli.Zsh()
    commands = ['food', 'cargo', 'flake8']

    shell.install(commands)

    assert mock_initialize
    assert mock_install_commands


@patch('cli.commands_not_installed', return_value=['cargo', 'food', 'flake8'])
def test_fish_install(mock_commands_not_installed):
    shell = cli.Fish()
    commands = ['food', 'cargo', 'flake8']

    m = mock_open(read_data='')
    with patch('cli.open', m):
        shell.install(commands)

    m.assert_called()


def test_powershell_install_file_path():
    shell = cli.PowerShell()

    result = shell.install_file_path
    assert str(result) == '/Users/radtomas/.config/powershell/Microsoft.PowerShell_profile.ps1'


# @mock.patch('cli.subprocess.check_output', return_value=True)
# @mock.patch('cli.PowerShell.exists', return_value=False)
# def test_powershell_install(mock_exists, mock_check_output):
#     shell = cli.PowerShell()
#
#     m = mock.mock_open(read_data='powershell_completer {python_script_path}')
#     with mock.patch('cli.open', m):
#         shell.install([])
#
#     m.assert_called()


#bash.py
def test_backends_bash():
    pass
