.. sufler documentation master file, created by
   sphinx-quickstart on Fri Mar  9 11:41:07 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Sufler
==================================

Sufler - is the tool to help you with generating bash/zsh/powershell/fish autocompletions from `YAML <https://en.wikipedia.org/wiki/YAML>`_ file.


.. raw:: html

    <iframe src="http://showterm.io/1e2c977b1a41c4f3f2076#fast" width="640" height="480"></iframe>

Quickstart
==========

.. _installation-guide:

Installation
------------

To install Sufler, open an interactive shell and run:

.. code::

    pip install sufler

or

.. code::

    bash -c "$(curl -fsSL https://raw.githubusercontent.com/limebrains/sufler/master/install.bash)"


Using Sufler
-------------

To start using **Sufler**, you need to first install completions.

.. code::

    $ sufler install

.. note::

    During installation. may appear message that ask for shell completer path if not detected automatically

You will have directory in your home dir where you can install your custom completions.

.. code::

    /Users/user/.sufler/
    ├── completions
    │   ├── npm.yml
    │   └── pip.yml
    └── .config

There is repo which accepts PR's with common completions `sufler-completions - github <https://github.com/limebrains/sufler-completions>`_

After installation just reload shell, type installed command and press double time **Tab**.

Creation of completion
======================

For example, we want to add completion for command **food**, so we need to add his arguments in nodes after **:**

.. code::

    'food': &food
        'fruit': &fruit
            'orange': *fruit
            'banana': *fruit
            'strawberry': *fruit
            'grape':
                'green':
                'red':
            'grapefruit':
                '"ruby red"':
                'yellow':
            '--seedless=': &seedless
                'true': *food
                'false': *food

            '<Exec> ls':
              'rm':

.. note:: We can add reference to any node of tree. E.g. if we want to repeat completions from **'fruit'** after **'orange'**,

Advanced
======================

Sufler has implemented support for advanced markers:

.. hlist::
    :columns: 1

    * **TREE**

        Tree marker can be used in any other place for access to previously selected elements from tree.

        .. code::

            'fruit': &fruit
                '<Exec> ls':
                  'cat':
                    '<Run> TREE~1 TREE~2':

        after

        .. code::

            'fruit': &fruit
                '<Exec> ls':
                  'cat':
                    '<Run> cat README.md':

    * **<File>**

        File marker allow to display in autocomplete all files in current directory.

        .. code::

            '-r':
                '<File>': *food

        after

        .. code::

            '-r':
                'Library/': *food
                'Desktop/': *food
                'Movies/': *food
                'Pictures/': *food
                'README.md': *food

        .. note:: File can autocomplete path to nested files if recursive parameter('<File rec>') is used.

    * **<Exec>**

        Exec mark allow to get output of shell commands as completion.

        .. code::

            'fruit': &fruit
                '-f':
                    '<Exec> ls /': *food

        after running the command it return

        .. code::

            'fruit': &fruit
                '-f':
                    'Library/': *food
                    'System/': *food
                    'Volumes/': *food
                    'etc/': *food
                    'Users/': *food

    * **<Regex>**

        Regex mark check take regular expression and check that entered string match to expression. If True return what nested node as completion else suggest current node.

        .. code::

            '--color':
                'red': *food
                'white': *food
                'blue': *food
                '<Regex>.+ack': *m

    * **<Run>**

        Run mark allow to run any option that will be executed by sufler. In example we use earlier selections to complete and execute command.

        .. code::

            'fruit': &fruit
                '<Exec> ls':
                  'cat':
                    '<Run> TREE~1 TREE~2':

        after

        .. code::

            $ fruit README.md cat &>/dev/null | sufler run 'cat README.md'

        In example we use output of *ls* command(README.md) and use *cat* command to display content on screen.
