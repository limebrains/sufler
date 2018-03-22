======================
Advanced
======================

Sufler has implemented support for advenced markers:

.. hlist::
    :columns: 1

    * **<File>**

        File marker allow to display in autocomplete all files in current directory.
        .. code::

            '-r':
                '<File>': *food

        .. note:: File can autocomplete path to nested files if used **rec** parameter('<File rec>').

    * **<Exec>**

        Exec mark allow to get output of shell commands as completion.
        .. code::

            'fruit': &fruit
                '-f':
                    '<Exec> ls /': *food

        .. note:: Shell command need to be after closed mark.


    * **<Regex>**

        Regex mark check that entered string match the expression. If True return what nested node as completion else suggest current node.

        .. code::

            '--color':
                'red': *food
                'white': *food
                'blue': *food
                '<Regex>.+ack': *m

    * **<Run>**

        Run mark allow to use earlier selections to complete and execute command.

        .. code::

            'fruit': &fruit
                '<Exec> ls':
                  'cat':
                    '<Run> TREE~1 TREE~2':

        In example we use output of *ls* command and use *cat* to display on screen.

        .. note:: In order to use the previous arguments, we can use TREE tags and the number given after '~'. The number refers to the previous items and starts at 1.