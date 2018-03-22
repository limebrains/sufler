from sufler import base

import pytest

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
