===================
sphinxnotes-snippet
===================

---------------------------------------------
Command line toolset for Sphinx documentation
---------------------------------------------

.. image:: https://img.shields.io/github/stars/sphinx-notes/khufu.svg?style=social&label=Star&maxAge=2592000
   :target: https://github.com/sphinx-notes/any

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
              'sphinxnotes.khufu.ext.snippet',
              # …
              ]

.. _Configuration:

Configuration
=============

The extension provides the following configuration:

TODO

Functionalities
===============

Change Log
==========

2021-02-01 1.0a1
----------------

- Dont evaluate typing annoations on runtime
- Speed up snippet cache
- Speed up title path resolving
- Better tokenizer
- A lot of bug fixes
- Add config khufu_snippet_patterns

.. sectionauthor:: Shengyu Zhang

2021-01-29 1.0a0
----------------


The alpha version is out, enjoy~

.. sectionauthor:: Shengyu Zhang
