from sufler.backends.bash import bash
from sufler.backends.fish import fish
from sufler.backends.powershell import powershell

import pytest
from mock import patch, call

#bash.py
@patch('sufler.backends.bash.bash.completion')
@patch('sufler.backends.bash.bash.print')
@pytest.mark.parametrize('test_data, expected_value', [
    ('options', 'options'),
    ({'test': 'some', 'data': 'thing'}, 'test\ndata'),
])
def test_backends_bash(mock_print, mock_completion, test_data, expected_value):
    mock_completion.return_value = test_data

    bash.bash_parse()

    assert mock_completion.call_count == 1
    mock_print.assert_called_with(expected_value)


#fish.py
@patch('sufler.backends.fish.fish.completion')
@patch('sufler.backends.fish.fish.print')
@pytest.mark.parametrize('test_data, expected_value', [
    ('options', 'options'),
    ({'test': 'some', 'data': 'thing'}, ['test', 'data']),
])
def test_backends_fish(mock_print, mock_completion, test_data, expected_value):
    mock_completion.return_value = test_data

    fish.fish_parse()

    calls = []
    if isinstance(test_data, dict):
        calls = [call(expected_value[0]), call(expected_value[1])]
    if isinstance(test_data, str):
        calls = [call(expected_value)]

    assert mock_completion.call_count == 1
    assert mock_print.mock_calls == calls


#powershell.py
@patch('sufler.backends.powershell.powershell.completion')
@patch('sufler.backends.powershell.powershell.print')
@pytest.mark.parametrize('test_data, expected_value', [
    ('options', 'options'),
    ({'test': 'some', 'data': 'thing'}, ['test', 'data']),
])
def test_backends_powershell(mock_print, mock_completion, test_data, expected_value):
    mock_completion.return_value = test_data

    powershell.powershell_parse()

    calls = []
    if isinstance(test_data, dict):
        calls = [call(expected_value[0]), call(expected_value[1])]
    if isinstance(test_data, str):
        calls = [call(expected_value)]

    assert mock_completion.call_count == 1
    assert mock_print.mock_calls == calls
