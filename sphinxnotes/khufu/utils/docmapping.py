"""
    sphinxnotes.utils.docstore
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    A customized persistent KV store for Sphinx project.

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
import os
from os import path
from typing import Dict, Set, Optional, Iterable, TypeVar
from datetime import datetime
import pickle
from collections.abc import MutableMapping

T = TypeVar('T') 

class Mapping(MutableMapping):
    """A customized persistent KV store for Sphinx project."""

    class Stat(object):
        last_update:datetime

        def __init__(self) -> None:
            self.last_update = None


    # The real in memory store of values
    _store:Dict[str,T]
    # Tree structure of values
    # Project -> Docname -> Keys
    tree:Dict[str,Dict[str,Set[str]]] # Real type: defaultdict
    # Ts that need write back to store
    _dirty_items:Dict[str,T]
    # Ts that need purge from store
    _orphan_items:Dict[str,T]


    def __init__(self, dirname:str) -> None:
        self.dirname = dirname
        self._store = {}
        self.tree = {}
        self._dirty_items = {}
        self._orphan_items = {}


    def __getitem__(self, key:str) -> Optional[T]:
        if not key in self._store:
            return None
        value = self._store[key]
        if value:
            return value
        # T haven't loaded yet, load it from disk
        with open(self.itemfile(key), 'rb') as f:
            value = pickle.load(f)
            self._store[key] = value
            return value


    def __setitem__(self, key:str, value:T) -> None:
        self._store[key] = value
        self._dirty_items[key] = value
        if key in self._orphan_items:
            del self._orphan_items[key]

        # Update tree
        if not value.project in self.tree:
            self.tree[value.project] = {}
        if not value.docname in self.tree[value.project]:
            self.tree[value.project][value.docname] = set()
        self.tree[value.project][value.docname].add(key)


    def __delitem__(self, key:str) -> None:
        value = self._store.pop(key)
        self._orphan_items[key] = value
        if key in self._dirty_items:
            del self._dirty_items[key]

        # Update tree
        self.tree[value.project][value.docname].remove(key)
        if len(self.tree[value.project][value.docname]) == 0:
            del self.tree[value.project][value.docname]
            if len(self.tree[value.project]) == 0:
                del self.tree[value.project]


    def __iter__(self) -> Iterable:
        return iter(self._store)


    def __len__(self) -> int:
        return len(self._store)


    def _keytransform(self, key:str) -> str:
        # No used
        return key


    def by_project(self, project:str) -> Set[str]:
        res = set()
        for _, keys in self.tree[project].items:
            res.update(keys)
        return res


    def by_docname(self, project:str, docname:str) -> Set[str]:
        return self.tree[project][docname].copy()


    def load(self) -> None:
        with open(self.cachefile(), 'rb') as f:
            obj = pickle.load(f)
            self.__dict__.update(obj.__dict__)


    def dump(self):
        """Dump store to disk."""
        # Makesure dir exists
        if not path.exists(self.dirname):
            os.mkdir(self.dirname)

        # Purge orphan items
        for key, value in self._orphan_items.items():
            os.remove(self.itemfile(key))
            self.post_purge(key, value)

        # Dump dirty items
        for key, value in self._dirty_items.items():
            with open(self.itemfile(key), 'wb') as f:
                pickle.dump(value, f)
            self.post_dump(key, value)

        # Clear all in-memory items
        self._orphan_items = {}
        self._dirty_items = {}
        self._store = {key: None for key in self.store}

        # Dump store itself
        with open(self.cachefile(), 'wb') as f:
            pickle.dump(self, f)


    def cachefile(self) -> str:
        return path.join(self.dirname, 'cache.pickle')


    def itemfile(self, key:str) -> str:
        return path.join(self.dirname, key + '.pickle')


    def post_dump(self, key:str,value:T) -> None:
        pass


    def post_purge(self, key:str,value:T) -> None:
        pass
