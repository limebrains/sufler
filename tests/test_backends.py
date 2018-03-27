import pytest
from mock import call, patch
from StringIO import StringIO
from sufler.backends.bash import bash
from sufler.backends.fish import fish
from sufler.backends.powershell import powershell


#bash.py
@patch('sufler.backends.bash.bash.completion')
@patch('sys.stdout')
@pytest.mark.parametrize('test_data, expected_value', [
    ('options', 'options'),
    ({'test': 'some', 'data': 'thing'}, 'test\ndata'),
])
def test_backends_bash(mock_print, mock_completion, test_data, expected_value):
    mock_completion.return_value = test_data
    mock_print.new_callable = StringIO

    bash.bash_parse()

    calls = []
    if isinstance(test_data, dict):
        calls = [
            call.write(expected_value),
            call.write('\n'),
        ]
    if isinstance(test_data, str):
        calls = [call.write(expected_value), call.write('\n')]

    assert mock_completion.call_count == 1
    assert mock_print.mock_calls == calls


#fish.py
@patch('sufler.backends.fish.fish.completion')
@patch('sys.stdout')
@pytest.mark.parametrize('test_data, expected_value', [
    ('options', 'options'),
    ({'test': 'some', 'data': 'thing'}, ['test', 'data']),
])
def test_backends_fish(mock_print, mock_completion, test_data, expected_value):
    mock_completion.return_value = test_data
    mock_print.new_callable = StringIO

    fish.fish_parse()

    calls = []
    if isinstance(test_data, dict):
        calls = [
            call.write(expected_value[0]),
            call.write('\n'),
            call.write(expected_value[1]),
            call.write('\n')
        ]
    if isinstance(test_data, str):
        calls = [call.write(expected_value), call.write('\n')]

    assert mock_completion.call_count == 1
    assert mock_print.mock_calls == calls


#powershell.py
@patch('sufler.backends.powershell.powershell.completion')
@patch('sys.stdout')
@pytest.mark.parametrize('test_data, expected_value', [
    ('options', 'options'),
    ({'test': 'some', 'data': 'thing'}, ['test', 'data']),
])
def test_backends_powershell(mock_print, mock_completion, test_data, expected_value):
    mock_completion.return_value = test_data
    mock_print.new_callable = StringIO

    powershell.powershell_parse()
    calls = []
    if isinstance(test_data, dict):
        calls = [
            call.write(expected_value[0]),
            call.write('\n'),
            call.write(expected_value[1]),
            call.write('\n')
        ]
    if isinstance(test_data, str):
        calls = [call.write(expected_value), call.write('\n')]

    assert mock_completion.call_count == 1
    assert mock_print.mock_calls == calls
