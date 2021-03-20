"""
    sphinxnotes.snippet.cli
    ~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import sys
import argparse
from typing import List
from os import path
from textwrap import dedent

from xdg.BaseDirectory import xdg_config_home

from . import __title__, __version__, __description__
from .config import Config
from .cache import Cache
from .filter import Filter
from .viewer import Viewer
from .editor import Editor

DEFAULT_CONFIG_FILE = path.join(xdg_config_home, __title__, 'conf.py')

class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                    argparse.RawDescriptionHelpFormatter): pass

def add_subcommand_common_arguments(parser:argparse.ArgumentParser, kinds:str) -> None:
    """Add common arguments (partial) subcommands to subcommands' argument parser."""
    parser.add_argument('keywords', nargs='*', help='keywords for pre-filtering')
    parser.add_argument('--id', nargs=1, help='specify snippet item by ID instead of filtering')
    parser.add_argument('--kinds', '-k', nargs=1, default=kinds, help='snippet kinds for pre-filtering')


def main(argv:List[str]=sys.argv[1:]) -> int:
    """Command line entrypoint."""

    parser = argparse.ArgumentParser(prog=__name__, description=__description__,
                                     # formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                     formatter_class=HelpFormatter,
                                     epilog=dedent("""
                                     snippet kinds:
                                       d (headline)          documentation title and possible subtitle
                                       c (code)              notes with code block
                                       p (procedure)         notes with a sequence of code for doing something (TODO)
                                       i (image)             notes with an image (TODO)
                                       * (any)               wildcard kind for any kind of snippet"""))
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-c', '--config', default=DEFAULT_CONFIG_FILE, help='path to configuration file')

    # Init subcommands
    subparsers = parser.add_subparsers()
    mgmtparser = subparsers.add_parser('mgmt', aliases=['m'], help='snippets management')
    mgmtparser.add_argument('--stat', '-s', action='store_true', help='show snippets statistic')
    mgmtparser.add_argument('--dump-config', '-d', action='store_true', help='dump current configuration')
    mgmtparser.add_argument('--dump-index', '-i', action='store_true', help='dump snippet indexes')
    mgmtparser.add_argument('--list', action='store_true', help='list all snippets')
    mgmtparser.add_argument('--purge', action='store_true', help='purge all snippets')
    mgmtparser.set_defaults(func=_on_command_mgmt)

    viewparser = subparsers.add_parser('view', aliases=['v'],
                                       help='filter and view snippet')
    viewparser.set_defaults(func=_on_command_view)

    editparser = subparsers.add_parser('edit', aliases=['e'],
                                       help='filter snippet and edit the corresponding source file')
    editparser.set_defaults(func=_on_command_edit)

    invokeparser = subparsers.add_parser('invoke', aliases=['i'],
                                         help='filter and invoke executable snippet')
    invokeparser.set_defaults(func=_on_command_invoke)

    clipparser = subparsers.add_parser('clip', aliases=['c'],
                                       help='filter and clip snippet to clipboard')
    clipparser.set_defaults(func=_on_command_clip)


    # Add common arguments
    # TODO: to be document?
    kinds = ['c', 'cd', 'c', 'c']
    for i, p in enumerate([viewparser, editparser, invokeparser, clipparser]):
        add_subcommand_common_arguments(p, kinds[i])

    # Parse command line arguments
    args = parser.parse_args(argv)

    # Load config from file
    if args.config == DEFAULT_CONFIG_FILE and not path.isfile(DEFAULT_CONFIG_FILE):
        print('the default configuration file does not exist, ignore it')
        cfg = Config({})
    else:
        cfg = Config.load(args.config)
    setattr(args, 'config', cfg)

    # Load snippet cache
    cache = Cache(cfg.cache_dir)
    cache.load()
    setattr(args, 'cache', cache)

    # Call subcommand
    if hasattr(args, 'func'):
        args.func(args)


def _on_command_mgmt(args:argparse.Namespace):
    cache = args.cache

    if args.stat:
        # Cache
        num_snippets = {}
        num_docs = {}
        for project, docname in cache.keys():
            num_docs[project] = num_docs.get(project, 0) + 1
            num_snippets[project] = num_snippets.get(project, 0) + len(cache[(project, docname)]) # FIXME
        print('snippets are loaded from %s' % cache.dirname)
        print(f'I have {len(num_docs)} project(s), {sum(num_docs.values())} documentation(s) and {sum(num_snippets.values())} snippet(s)')
        for i in num_docs:
            print(f'project {i}:')
            print(f"\t {num_docs[i]} documentation(s), {num_snippets[i]} snippets(s)")
    if args.dump_config:
        # Configuration
        print('configuration are loaded from %s' % args.config.__file__)
        for k,v in args.config.__dict__.items():
            if k.startswith('__'):
                continue
            print('%s:\t\t%s' % (k, v))
    if args.dump_index:
        print('snippet index are loaded from %s' % args.cache.dictfile())
        for k, v in args.cache.indexes.items():
            print(k, v)

    # Snippet related
    if args.list:
        for doc_id, item_list in cache.items():
            for item_offset, item in enumerate(item_list):
                print((doc_id, item_offset)) # TODO: list snippet content?
    if args.purge:
        cache.clear()
        cache.dump()


def _on_command_view(args:argparse.Namespace):
    filter = Filter(args.cache, args.config)
    item = filter.filter(keywords=args.keywords, kinds=args.kinds)
    if not item:
        return
    viewer = Viewer(args.config)
    viewer.view(item.snippet)


def _on_command_edit(args:argparse.Namespace):
    filter = Filter(args.cache, args.config)
    item = filter.filter(keywords=args.keywords, kinds=args.kinds)
    if not item:
        return
    editor = Editor(args.config)
    editor.edit(item.snippet)


def _on_command_invoke(args:argparse.Namespace):
    pass


def _on_command_clip(args:argparse.Namespace):
    pass


if __name__ == '__main__':
    sys.exit(main())
