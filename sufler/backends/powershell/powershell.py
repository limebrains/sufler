#!/usr/bin/env python3

import sys

from sufler.base import completion


def powershell_parse():
    list_of_arguments = [sys.argv[0]]
    arguments = list(
                    item
                    for item in sys.argv[1].split(' ') if item
                    )
    list_of_arguments.append(len(arguments))
    list_of_arguments += arguments

    options = completion(
        command_name=list_of_arguments[2],
        all_arguments=list_of_arguments,
    )

    if isinstance(options, dict):
        for item in options.keys():
            print(item)
    if isinstance(options, str):
        print(options)


if __name__ == "__main__":
    powershell_parse()
