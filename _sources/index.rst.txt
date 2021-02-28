===================
sphinxnotes-snippet
===================

------------------------------------------------------
Non-intrusive snippet manager for Sphinx documentation
------------------------------------------------------

.. image:: https://img.shields.io/github/stars/sphinx-notes/snippet.svg?style=social&label=Star&maxAge=2592000
   :target: https://github.com/sphinx-notes/snippet

:version: |version|
:copyright: Copyright ©2021 by Shengyu Zhang.
:license: BSD, see LICENSE for details.

.. contents::
   :local:
   :backlinks: none

Installation
============

Download it from official Python Package Index:

.. code-block:: console

   $ pip install sphinxnotes-snippet

Add extension to :file:`conf.py` in your sphinx project:

TODO

.. code-block:: python

    extensions = [
              # …
              'sphinxnotes.snippet.ext',
              # …
              ]


.. _Configuration:

Extension
=========

Configuration
-------------

The extension provides the following configuration:

:snippet_config: (Type: ``Dict[str,Any]``, Default: ``{}``)
                 Configuration of snippet cli command.

:snippet_patterns: (Type: ``Dict[str,List[str]]``, Default: ``{}``)


Command Line Tool
=================

A python script named :file:`snippet` should be installed in your path.
(Usually :file:`/usr/local/bin` or :file:`~/.local/bin`).

Invoke ``snippet --help`` for usage.

Change Log
==========

2021-02-28 1.0b1
----------------

.. sectionauthor:: Shengyu Zhang

- Refactor!!!
- Rename from sphinxnotes-khufu

2021-02-01 1.0a1
----------------

.. sectionauthor:: Shengyu Zhang

- Dont evaluate typing annoations on runtime
- Speed up snippet cache
- Speed up title path resolving
- Better tokenizer
- A lot of bug fixes
- Add config khufu_snippet_patterns

2021-01-29 1.0a0
----------------

.. sectionauthor:: Shengyu Zhang

The alpha version is out, enjoy~
