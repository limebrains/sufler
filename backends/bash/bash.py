import sys

from base import completion

if __name__ == "__main__":
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
