#!/usr/bin/env python3

import logging
import os

import re
import subprocess
import yaml

logger = logging.getLogger(__file__)

SUFLER_BASE_PATH = os.path.abspath(os.path.dirname(__file__))
os.environ['SUFLER_HOME'] = SUFLER_BASE_PATH


def get_files_autocomplete(already_typed):
    """ Get files list for <File> marker in .yml file

    :param already_typed: Already typed string
    :return: List of files in directory or already typed path to file
    """
    if os.path.exists(already_typed) and os.path.isfile(already_typed):
            return [already_typed]

    path = '/'.join(already_typed.split('/')[:-1])
    try:
        res = list(map(
            lambda file:
            file + '/'
            if os.path.isdir(file)
            else
            file, os.listdir('{0}/{1}'.format(os.getcwd(), path))
        ))
    except OSError:
        res = [already_typed]
    return res


def get_autocomplete_file_for_command(command):
    """ Read completion for command from .yml file

    :param command: The command for which read completions
    :return: Dict of completions for command
    """
    path_to_command = os.path.expanduser(
        '~/.sufler/completions/{0}.yml'.format(command)
    )
    return yaml.load_all(open(path_to_command, "r"))


def replace_tree_marks(key, arguments):
    """ Replace TREE markers from key to proper argument

    :param key: The currently processed key from .yaml file
    :param arguments: Arguments already typed for command
    :return: Key string with replaced marks
    """
    tree_mark_index = key.find('TREE~')
    while tree_mark_index >= 0:

        tree_index = -int(key[tree_mark_index+5])

        key = key[:tree_mark_index] \
            + arguments[tree_index] \
            + key[tree_mark_index+6:]

        tree_mark_index = key.find('TREE~')

    return key


def completion(command_name, all_arguments):
    """ Parse already typed arguments for command and return matching arguments

    :param command_name: Command for which we make completion
    :param all_arguments: Arguments already typed for command
    :return: Dict with matching arguments
    """
    autocomplete_dict = get_autocomplete_file_for_command(command_name)
    root = list(autocomplete_dict)[0]

    number_of_arguments = int(all_arguments[1])
    rest_arguments = all_arguments[2:]

    if number_of_arguments == 0:
        return root

    for i, argument in enumerate(rest_arguments):
        try:
            root = root[argument]
        except KeyError:
            try:
                root = root[argument + ' ']
            except KeyError:
                return root

        if not isinstance(root, dict):
            break

        current_keys = list(root.keys())
        next_argument = rest_arguments[i + 1] \
            if i + 1 < len(rest_arguments) else None

        for key in current_keys:

            old_key = key
            key = replace_tree_marks(key, rest_arguments)

            if key.startswith('<File'):
                recursive = True if 'rec' in key else False

                already_typed = next_argument \
                    if next_argument and recursive else argument
                files_matching = get_files_autocomplete(already_typed)
                rest_of_tree = root.pop(key)
                root.update({
                    file_matching: rest_of_tree
                    for file_matching in files_matching
                })

            if key.startswith('<Exec'):
                try:
                    autocomplete_from_command = subprocess.check_output(
                        key.replace('<Exec>', ''), shell=True).decode('utf-8')
                except subprocess.CalledProcessError:
                    autocomplete_from_command = ''
                rest_of_tree = root.pop(old_key)
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

            if key.startswith('<Run'):
                end_command = key.replace('<Run>', '')
                print(r'&>/dev/null |  sufler run \"{end_command}\"'.format(
                    end_command=end_command)
                )
                root = {}

    return root
