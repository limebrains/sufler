from sufler import base

import pytest
import mock

@pytest.mark.parametrize('file, expected_value', [
    ('sufler/base.py', ['sufler/base.py']),
    ('docs/', ['index.rst',
               '.DS_Store',
               '_templates',
               'Makefile',
               'conf.py',
               '_static',
               'user',
               'make.bat',
               '_build',
               'modules'
               ]),
])
def test_get_files_autocomplete(file, expected_value):
    assert base.get_files_autocomplete(file) == expected_value


@mock.patch('sufler.base.yaml.load_all', return_value={'Yep': 'pancake'})
def test_autocomplete_file_for_command(mock_load_all):
    m = mock.mock_open(read_data="'Yep': 'pancake':")
    with mock.patch('sufler.base.open', m):
        autocomplete_dict = base.get_autocomplete_file_for_command('food')
    assert isinstance(autocomplete_dict, dict)
    mock_load_all.assert_called_once()


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
