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
from .table import tablify, VISIABLE_COLUMNS

DEFAULT_CONFIG_FILE = path.join(xdg_config_home, __title__, 'conf.py')

class HelpFormatter(argparse.ArgumentDefaultsHelpFormatter,
                    argparse.RawDescriptionHelpFormatter): pass


def main(argv:List[str]=sys.argv[1:]) -> int:
    """Command line entrypoint."""

    parser = argparse.ArgumentParser(prog=__name__, description=__description__,
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
    mgmtparser = subparsers.add_parser('stat',
                                       aliases=['s'],
                                       formatter_class=HelpFormatter,
                                       help='snippets statistic')
    mgmtparser.set_defaults(func=_on_command_mgmt)

    listparser = subparsers.add_parser('list',
                                       aliases=['l'],
                                       formatter_class=HelpFormatter,
                                       help='list snippet indexes, columns of indexes: %s' %
                                       VISIABLE_COLUMNS)
    listparser.add_argument('--kinds', '-k',
                            action='store_true',
                            default='*',
                            help='list specified kinds only')
    listparser.add_argument('--width', '-w',
                            action='store_true',
                            default=120,
                            help='width in characters of output')
    listparser.set_defaults(func=_on_command_list)

    getparser = subparsers.add_parser('get',
                                      aliases=['g'],
                                      formatter_class=HelpFormatter,
                                      help='get information of snippet by index ID')
    getparser.add_argument('--file', '-f',
                           action='store_true',
                           help='get source file path of snippet')
    getparser.add_argument('--text', '-t',
                           action='store_true',
                           default=True,
                           help='get source reStructuredText of snippet')
    getparser.add_argument('index_id',
                           type=str,
                           nargs='+',
                           help='index ID')
    getparser.set_defaults(func=_on_command_get)

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

    num_projects = len(cache.num_snippets_by_project)
    num_docs = len(cache.num_snippets_by_docid)
    num_snippets = sum(cache.num_snippets_by_project.values())
    print(f'snippets are loaded from {cache.dirname}')
    print(f'I have {num_projects} project(s), {num_docs} documentation(s) and {num_snippets} snippet(s)')
    for i, v in cache.num_snippets_by_project.items():
        print(f'project {i}:')
        print(f"\t {v} snippets(s)")


def _on_command_list(args:argparse.Namespace):
    rows = tablify(args.cache.indexes, args.kinds, args.width)
    for row in rows:
        print(row)


def _on_command_get(args:argparse.Namespace):
    for index_id in args.index_id:
        item = args.cache.get_by_index_id(index_id)
        if not item:
            print('no such index ID', file=sys.stderr)
            sys.exit(1)
        if args.file:
            print(item.snippet.file())
        if args.text:
            print('\n'.join(item.snippet.text()))


if __name__ == '__main__':
    sys.exit(main())