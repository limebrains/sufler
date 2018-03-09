#!/usr/bin/env python3

import logging
import os

import yaml, subprocess, re, pathlib

logger = logging.getLogger(__file__)

SUFLER_BASE_PATH = os.path.abspath(os.path.dirname(__file__))
os.environ['SUFLER_HOME'] = SUFLER_BASE_PATH


def get_files_autocomplete(already_typed):
    """ Get files list for <File> marker in .yml file

    :param already_typed: Already typed string
    :return: List of files in directory or already typed path to file
    """
    path = pathlib.Path(already_typed)
    if path.exists() and path.is_file():
            return [already_typed]

    path = pathlib.Path('/'.join(already_typed.split('/')[:-1]))
    res = map(lambda file: str(file) + '/' if file.is_dir() else str(file), list(path.glob('*')))
    return res


def get_autocomplete_file_for_command(command):
    """"""
    path_to_command = os.path.abspath(os.path.join(os.path.dirname(__file__), 'completions', '{0}.yml'.format(command)))
    return yaml.load_all(open(path_to_command, "r"))


def completion(command_name, all_arguments):
    autocomplete_dict = get_autocomplete_file_for_command(command_name)
    root = list(autocomplete_dict)[0]

    number_of_arguments, rest_arguments = int(all_arguments[1]), all_arguments[2:]

    if number_of_arguments == 0:
        return root

    for i, argument in enumerate(rest_arguments):
        try:
            root = root[argument]
        except KeyError:
            try:
                root = root[argument + ' ']
            except KeyError:
                continue

        if not isinstance(root, dict):
            break
            # TODO : maybe support running collected command in shell

        current_keys = list(root.keys())
        next_argument = rest_arguments[i + 1] if i + 1 < len(rest_arguments) else None

        for key in current_keys:
            if key.startswith('<File'):
                recursive = False if 'rec' in key else True

                already_typed = next_argument if next_argument and recursive else argument
                files_matching = get_files_autocomplete(already_typed)
                rest_of_tree = root.pop(key)
                root.update({
                    file_matching: rest_of_tree
                    for file_matching in files_matching
                })

            if key.startswith('<Exec'):
                autocomplete_from_command = subprocess.check_output(
                    key.replace('<Exec>', '').replace('TREE~2', rest_arguments[i - 1]), shell=True).decode('utf-8')
                rest_of_tree = root.pop(key)
                if not rest_of_tree:
                    return autocomplete_from_command

                root.update({
                    item: rest_of_tree
                    for item in autocomplete_from_command.split('\n')
                })

            if key.startswith('<Regex') and next_argument:
                pattern = re.compile(key.replace('<Regex>', ''))
                rest_of_tree = root.pop(key)

                if re.search(pattern, next_argument):
                    root.update({
                        next_argument: rest_of_tree
                    })

    return root
