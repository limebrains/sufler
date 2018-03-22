.. sufler documentation master file, created by
   sphinx-quickstart on Fri Mar  9 11:41:07 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Sufler
==================================

Sufler provides the ability to easily add new completions for commands.



The tool use completions for commands from .yml files.
Sufler support shells:

.. hlist::
    :columns: 1

    * Bash
    * Fisch
    * Zsh
    * Powershell

Quickstart
==========

.. _installation-guide:

Installation
------------

To install Sufler, open an interactive shell and run:

.. code::

    bash -c "$(curl -fsSL https://raw.githubusercontent.com/limebrains/sufler/master/install.bash)"

Or to specify installation directory and type of shell:

.. code::

    bash -c "shell='bash_or_zsh';install_dir='absolute_path';$(curl -fsSL https://raw.githubusercontent.com/limebrains/sufler/master/install.bash)"

Using Sufler
-------------

After installation just type command you like and press **Tab**.


.. toctree::
   :maxdepth: 2

   user/index
   modules/index
