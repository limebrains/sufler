======================
Advanced Markers
======================

Sufler has implemented support for advenced markers:

.. hlist::
    :columns: 1

    * **<File>**
    .. note:: File return files in current working directory.

    * **<Exec>**
    .. note:: Mark Exec allow to get as completion result of command writen after mark.
    .. code::

        'fruit': &fruit
            '-f':
                '<Exec> ls /': *food

    * **<Regex>**

