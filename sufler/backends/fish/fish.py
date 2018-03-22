#!/usr/bin/env python3

from sufler.base import completion
import sys


def fish_parse():
    list_of_arguments = [sys.argv[0]]
    arguments = list(
                    item
                    for item in sys.argv[1].split(' ')
                    if item
                    )
    # arguments = sys.argv[1]
    list_of_arguments.append(len(arguments))
    list_of_arguments += arguments

    options = completion(
        command_name=list_of_arguments[2],
        all_arguments=list_of_arguments,
    )

    # TODO : correct display for keys with spaces
    if isinstance(options, dict):
        for item in options.keys():
            print(item.replace('"', r'"'))
    if isinstance(options, str):
        print(options)


if __name__ == "__main__":
    fish_parse()
