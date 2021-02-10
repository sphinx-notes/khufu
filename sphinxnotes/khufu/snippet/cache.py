""" sphinxnotes.khufu.snippet.cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import os
from os import path
from typing import List, Tuple
from dataclasses import dataclass

# from rst2ansi import rst2ansi
# TODO: fix rst2ansi

from .import Snippet, Notes
from ..utils.docmapping import Mapping


@dataclass(frozen=True)
class Item(object):
    """ Item of snippet cache. """
    # Name of sphinx project
    project:str # TODO
    # Name of documentation
    docname:str
    titlepath:List[str]
    snippet:Snippet
    # (Keywords, Rank)
    keywords:List[Tuple[str,float]]

    def hexdigest(self) -> str:
        from hashlib import sha1
        hasher = sha1()
        # TODO: none for now
        if self.project:
            hasher.update(self.project.encode())
        hasher.update(self.docname.encode())
        [hasher.update(title.encode()) for title in self.titlepath]
        [hasher.update(line.encode()) for line in self.snippet.rst()]
        [hasher.update(keyword.encode()) for keyword, _ in self.keywords]
        return hasher.hexdigest()


class Cache(Mapping):
    """Cache of snippet."""
    # Path to directory for saving cache
    def __init__(self, dirname:str) -> None:
        super().__init__(dirname)


    def dump(self):
        """Overwrite Mapping.dump."""
        self._update_index()
        super().dump()


    def post_dump_item(self, key:str,item:Item) -> None:
        """Overwrite Mapping.post_dump."""
        with open(self.previewfile(key), 'w') as f:
            f.write('\n'.join(item.snippet.rst()))


    def post_purge_item(self, key:str, item:Item) -> None:
        """Overwrite Mapping.post_purge."""
        os.remove(self.previewfile(key))


    def indexfile(self) -> str:
        return path.join(self.dirname, 'index.txt')


    def previewfile(self, key:str) -> str:
        return path.join(self.dirname, key + '.rst')


    def add(self, item:Item) -> str:
        """Add item to cache, return ID of item"""
        digest = item.hexdigest()[:7]
        self[digest] = item
        return digest


    def purge_doc(self, project:str, docname:str) -> None:
        """Pure persistent items that belongs to given docname. """
        for k in self.by_docname(project, docname):
            del self[k]


    def _update_index(self) -> str:
        from ..utils.titlepath_extra import join
        ELLIPSIS = '...'
        lines = []
        for key, item in self.items():
            # TODO: responsive support?
            titlepath = join(item.titlepath, 50, 30,
                             placeholder=ELLIPSIS, reverse=True)
            if isinstance(item.snippet, Notes):
                excerpt = item.snippet.excerpt()
            else:
                excerpt = '<no excerpt available>'
            keywords = [keyword for keyword, rank in item.keywords]
            lines.append([key, excerpt, titlepath,  ','.join(keywords)])

        from tabulate import tabulate
        table = tabulate(lines,
                         headers=['ID', 'Excerpt' ,'Path',  'Keywords'],
                         tablefmt='plain')
        with open(self.indexfile(), 'w') as f:
            f.write(table)
