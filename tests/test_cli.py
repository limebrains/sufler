from sufler import cli

import pytest
from mock import patch, mock_open
from click import testing

def test_detect_shells():
    for shell in cli.detect_shells():
        assert isinstance(type(shell), type(cli.BaseShell))


@pytest.mark.parametrize('commands, completer_content, expected_values', [
    (['food', 'cargo'], 'Lorem food ipsum cargo', []),
    (['test', 'cargo'], 'Lorem test ipsum cos', ['cargo'])
])
def test_commands_not_installed(commands, completer_content, expected_values):
    assert cli.commands_not_installed(commands, completer_content) == expected_values


@patch('sufler.cli.os.listdir', return_value=['food.yml', 'cargo.yml', 'flake8.yml'])
def test_get_commands(mock_listdir):
    assert cli.get_commands() == ['food', 'cargo', 'flake8']
    mock_listdir.assert_called_once()


@patch('sufler.cli.get_completions_directory_from_git')
@patch('sufler.cli.os.path.expanduser', return_value='')
@patch('sufler.cli.os.listdir', side_effect=['pip', 'food'])
@patch('sufler.cli.shutil.copyfile')
def test_install_completion_files(
        mock_copyfile,
        mock_listdir,
        mock_expand,
        mock_get_completions):

    cli.install_completion_files()

    mock_copyfile.assert_called()
    mock_listdir.assert_called()
    mock_expand.assert_called()
    assert len(mock_expand.mock_calls) == 5
    mock_get_completions.assert_called()


@patch('sufler.cli.detect_shells', return_value=[
    cli.Bash(),
    cli.Fish(),
    cli.Zsh(),
    cli.PowerShell(),
])
@patch('sufler.cli.get_commands', return_values=[
    'cargo',
    'food',
    'flake8',
])
@patch('sufler.cli.BaseShell.install')
def test_install_command(mock_install, mock_get_commands, mock_detect_shells):
    result = testing.CliRunner().invoke(cli.install_command)

    assert result.exit_code == 0
    assert len(mock_get_commands.mock_calls) == 4
    mock_install.called_once()
    mock_detect_shells.assert_called_once()


@patch('sufler.cli.os.path.exists', return_value=False)
@patch('sufler.cli.os.mkdir')
@patch('sufler.cli.os.path.expanduser', return_value='')
@patch('sufler.cli.yaml.dump')
def test_init_command(mock_dump, mock_expanduser, mock_mkdir, mock_exists):
    m = mock_open()
    with patch('sufler.cli.open', m):
        result = testing.CliRunner().invoke(cli.init_command)

    assert result.exit_code == 0
    mock_dump.assert_called_once()
    mock_expanduser.assert_called_once_with('~')
    mock_mkdir.assert_called()
    mock_exists.assert_called()


@pytest.mark.parametrize('command', [
    ['run ls'],
    ['run echo "cos"']
])
def test_run_command(command):
    result = testing.CliRunner().invoke(cli.run_command, command)
    assert result.exit_code == 0


SHELL_LIST = [
    (cli.SHELL_NAME_TO_CLASS['bash'], cli.PATH_FOR_SHELL['bash']),
    (cli.SHELL_NAME_TO_CLASS['fish'], cli.PATH_FOR_SHELL['fish']),
    (cli.SHELL_NAME_TO_CLASS['zsh'], cli.PATH_FOR_SHELL['zsh']),
    (cli.SHELL_NAME_TO_CLASS['powershell'], cli.PATH_FOR_SHELL['powershell']),
]


@pytest.mark.parametrize('shell_to_class, expected_values', SHELL_LIST)
def test_base_shell_get_install_path(shell_to_class, expected_values):
    shell = shell_to_class()
    assert shell.get_install_path() == expected_values[0]


@pytest.mark.parametrize('shell_to_class, expected_values', SHELL_LIST)
def test_base_shell_install_path(shell_to_class, expected_values):
    shell = shell_to_class()
    assert shell.install_path == expected_values[0]


@pytest.mark.parametrize('shell_to_class, expected_values', SHELL_LIST[:-1])
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
    with patch('sufler.cli.open', m):
        shell.install_commands(commands)

    assert 'bash_completer cargo food \\ncomplete -F _completer -o default flake8' in str(m.mock_calls[6])


def test_bash_shell_initialize():
    shell = cli.Bash()

    m = mock_open(read_data='bash_completer {python_script_path}')
    with patch('sufler.cli.open', m):
        shell.initialize()

    assert 'bash_completer /Users/radtomas/PycharmProjects/sufler/sufler/backends/bash/bash.py' in str(m.mock_calls[6])


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

@patch('sufler.cli.subprocess.check_output')
def test_zsh_shell_initialize(mock_check_output):
    shell = cli.Zsh()

    m = mock_open(read_data='bash_completer')

    with patch('sufler.cli.open', m):
        shell.initialize()

    assert 'bash_completer' in str(m.mock_calls[10])
    mock_check_output.called_once()


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


@patch('sufler.cli.commands_not_installed', return_value=['cargo', 'food', 'flake8'])
def test_fish_shell_install(mock_commands_not_installed):
    shell = cli.Fish()
    commands = ['food', 'cargo', 'flake8']

    m = mock_open(read_data='')
    with patch('sufler.cli.open', m):
        shell.install(commands)

    m.assert_called()
    mock_commands_not_installed.assert_called_once()


def test_powershell_install_file_path():
    shell = cli.PowerShell()

    result = shell.install_file_path
    assert str(result) == '/Users/radtomas/.config/powershell/Microsoft.PowerShell_profile.ps1'


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
