import os
import pytest
from click import testing
from mock import mock_open, patch

from sufler import cli

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


@patch('sufler.cli.os.path.exists', return_value=False)
@patch('sufler.cli.input', return_value='')
def test_detect_shells(mock_input, mock_exists):
    for shell in cli.detect_shells():
        assert isinstance(type(shell), type(cli.BaseShell))
    mock_exists.assert_called()
    mock_input.assert_called()


@pytest.mark.parametrize('commands, completer_content, expected_values', [
    (['food', 'cargo'], 'Lorem food ipsum cargo', []),
    (['test', 'cargo'], 'Lorem test ipsum cos', ['cargo'])
])
def test_commands_not_installed(commands, completer_content, expected_values):
    assert cli.commands_not_installed(commands, completer_content) == expected_values


@patch('sufler.cli.os.path.isfile', return_value=True)
@patch('sufler.cli.os.listdir', return_value=['food.yml', 'cargo.yml', 'flake8.yml'])
def test_get_commands(mock_listdir, mock_isfile):
    assert cli.get_commands(None) == ['food', 'cargo', 'flake8']
    assert cli.get_commands('pip') == ['pip']
    assert len(mock_listdir.mock_calls) == 2
    mock_isfile.assert_called()


@patch('sufler.cli.get_completions_directory_from_git')
@patch('sufler.cli.os.path.expanduser', return_value='')
@patch('sufler.cli.os.listdir', side_effect=['pip', 'food'])
@patch('sufler.cli.shutil.copyfile')
@patch('sufler.cli.shutil.rmtree')
def test_install_completion_files(
        mock_rmtree,
        mock_copyfile,
        mock_listdir,
        mock_expand,
        mock_get_completions):

    cli.install_completion_files()

    mock_rmtree.assert_called_once_with('')
    mock_copyfile.assert_called()
    mock_listdir.assert_called()
    mock_expand.assert_called()
    assert len(mock_expand.mock_calls) == 6
    mock_get_completions.assert_called()


SHELL_LIST = [
    (cli.SHELL_NAME_TO_CLASS['bash'], cli.PATH_FOR_SHELL['bash']),
    (cli.SHELL_NAME_TO_CLASS['fish'], cli.PATH_FOR_SHELL['fish']),
    (cli.SHELL_NAME_TO_CLASS['zsh'], cli.PATH_FOR_SHELL['zsh']),
    (cli.SHELL_NAME_TO_CLASS['powershell'], cli.PATH_FOR_SHELL['powershell']),
]


@patch('sufler.cli.os.path.exists', return_value=True)
@pytest.mark.parametrize('shell_to_class, expected_values', SHELL_LIST)
def test_base_shell_get_install_path(mock_exists, shell_to_class, expected_values):
    shell = shell_to_class()
    assert shell.get_install_path() == expected_values[0]
    mock_exists.assert_called()


@patch('sufler.cli.BaseShell.get_install_path', return_value='something')
@pytest.mark.parametrize('shell_to_class, expected_values', SHELL_LIST)
def test_base_shell_install_path(mock_get_install_path, shell_to_class, expected_values):

    shell = shell_to_class()

    assert shell.install_path == 'something'
    mock_get_install_path.assert_called()


@patch('sufler.cli.BaseShell.get_install_path', return_value='something')
@pytest.mark.parametrize('shell_to_class, expected_values', SHELL_LIST[:-1])
def test_base_shell_install_file_path(mock_get_install_path, shell_to_class, expected_values):

    shell = shell_to_class()

    assert str(shell.install_file_path) == 'somethingcompleter'
    mock_get_install_path.assert_called()


@patch('sufler.cli.BaseShell.get_install_path', return_value='not empty string')
@pytest.mark.parametrize('shell_to_class', [
    (cli.SHELL_NAME_TO_CLASS['bash']),
    (cli.SHELL_NAME_TO_CLASS['fish']),
    (cli.SHELL_NAME_TO_CLASS['zsh']),
    (cli.SHELL_NAME_TO_CLASS['powershell']),
])
def test_base_shell_exists(mock_get_install_path, shell_to_class):
    shell = shell_to_class()
    assert shell.exists()
    mock_get_install_path.assert_called()


@patch('sufler.cli.input', return_value='')
@pytest.mark.parametrize('shell_to_cls', [
    (cli.SHELL_NAME_TO_CLASS['bash']),
    (cli.SHELL_NAME_TO_CLASS['zsh']),
])
def test_bash_zsh_install_commands(mock_input, shell_to_cls):
    shell = shell_to_cls()
    commands = ['food', 'cargo', 'flake8']

    m = mock_open(read_data='bash_completer cargo food ')
    with patch('sufler.cli.open', m):
        shell.install_commands(commands)

    assert 'bash_completer cargo food \\ncomplete -F _completer -o default flake8' in str(m.mock_calls[6])
    # mock_input.assert_called()


@patch('sufler.cli.os.path.exists', return_value=True)
def test_bash_shell_initialize(mock_exists):
    shell = cli.Bash()

    m = mock_open(read_data='bash_completer {python_script_path}')
    with patch('sufler.cli.open', m):
        shell.initialize()

    assert m.call_count == 2
    mock_exists.assert_called()


@patch('sufler.cli.Bash.get_install_path', return_value='')
@patch('sufler.cli.os.path.exists', return_value=False)
@patch('sufler.cli.Bash.initialize')
@patch('sufler.cli.Bash.install_commands')
def test_bash_shell_install(mock_install_commands, mock_initialize, mock_exists, mock_get_install_path):
    shell = cli.Bash()
    commands = ['food', 'cargo', 'flake8']

    shell.install(commands)

    mock_install_commands.assert_called_once_with(commands)
    mock_initialize.assert_called_once()
    mock_exists.assert_called_once()
    mock_get_install_path.assert_called()


@patch('sufler.cli.Zsh.get_install_path', return_value='')
@patch('sufler.cli.subprocess.check_output')
def test_zsh_shell_initialize(mock_check_output, mock_get_install_path):
    shell = cli.Zsh()

    m = mock_open(read_data='bash_completer')

    with patch('sufler.cli.open', m):
        shell.initialize()

    assert 'bash_completer' in str(m.mock_calls[10])
    mock_check_output.called_once()
    mock_get_install_path.assert_called()


@patch('sufler.cli.Zsh.get_install_path', return_value='')
@patch('sufler.cli.os.path.exists', return_value=False)
@patch('sufler.cli.Zsh.initialize')
@patch('sufler.cli.Zsh.install_commands')
def test_zsh_shell_install(mock_install_commands, mock_initialize, mock_exists, mock_get_install_path):
    shell = cli.Zsh()
    commands = ['food', 'cargo', 'flake8']

    shell.install(commands)

    mock_install_commands.assert_called_once_with(commands)
    mock_initialize.assert_called_once()
    mock_exists.assert_called_once()
    mock_get_install_path.assert_called_once()


@patch('sufler.cli.input', return_value='')
@patch('sufler.cli.os.listdir', return_value='')
@patch('sufler.cli.commands_not_installed', return_value=['cargo', 'food', 'flake8'])
def test_fish_shell_install(mock_commands_not_installed, mock_listdir, mock_input):
    shell = cli.Fish()
    commands = ['food', 'cargo', 'flake8']

    m = mock_open(read_data='')
    with patch('sufler.cli.open', m):
        shell.install(commands)

    m.assert_called()
    mock_commands_not_installed.assert_called_once()
    mock_listdir.assert_called()
    mock_input()


@patch('sufler.cli.PowerShell.get_install_path', return_value='/Users/radtomas/.config/powershell/')
def test_powershell_install_file_path(mock_install_path):
    shell = cli.PowerShell()

    result = shell.install_file_path
    assert str(result) == '/Users/radtomas/.config/powershell/Microsoft.PowerShell_profile.ps1'
    mock_install_path.assert_called()


@patch('sufler.cli.PowerShell.get_install_path', return_value='')
@patch('sufler.cli.os.path.exists', return_value=False)
@patch('sufler.cli.subprocess.check_output')
def test_powershell_install(mock_check_output, mock_exists, mock_get_install_path):
    shell = cli.PowerShell()

    m = mock_open(read_data='powershell_completer')
    with patch('sufler.cli.open', m):
        shell.install([])

    assert m.call_count == 2
    assert mock_check_output.call_count == 2
    assert mock_exists.call_count == 2
    assert mock_get_install_path.call_count == 2
