import sys

from sufler.base import completion


def bash_parse():
    """ Pare arguments to list for completer function

        """
    options = completion(
        command_name=sys.argv[2],
        all_arguments=sys.argv,
    )

    if isinstance(options, dict):
        print('\n'.join(list(
            opt.replace('"', '\"') for opt in options.keys()
        )))
    if isinstance(options, str):
        print(options)


if __name__ == "__main__":
    bash_parse()
