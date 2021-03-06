"""
    sphinxnotes.snippet
    ~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2020 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Tuple, Optional, Any, Dict
from dataclasses import dataclass, field
from abc import ABC, abstractclassmethod
import itertools

from docutils import nodes


__title__= 'sphinxnotes-snippet'
__license__ = 'BSD',
__version__ = '1.0b6'
__author__ = 'Shengyu Zhang'
__url__ = 'https://sphinx-notes.github.io/snippet'
__description__ = 'Non-intrusive snippet manager for Sphinx documentation'
__keywords__ = 'documentation, sphinx, extension, utility'

@dataclass
class Snippet(ABC):
    """
    Snippet is a {abstract,data}class represents a snippet of reStructuredText
    documentation. Note that it is not always continuous fragment at text (rst)
    level.
    """
    _scope:Tuple[int,int] = field(init=False)
    _refid:Optional[str] = field(init=False)

    def __post_init__(self) -> None:
        """Post-init processing routine of dataclass"""

        # Calcuate scope before deepcopy
        scope = [float('inf'), -float('inf')]
        for node in self.nodes():
            if not node.line:
                continue # Skip node that have None line, I dont know why :'(
            scope[0] = min(scope[0], line_of_start(node))
            scope[1] = max(scope[1], line_of_end(node))
        self._scope = scope

        # Find exactly one id attr in nodes
        self._refid = None
        for node in self.nodes():
            if node['ids']:
                self._refid = node['ids'][0]
                break
        # If no node has id, use parent's
        if not self._refid:
            for node in self.nodes():
                if node.parent['ids']:
                    self._refid = node.parent['ids'][0]
                    break


    @abstractclassmethod
    def nodes(self) -> List[nodes.Node]:
        """Return the out of tree nodes that make up this snippet."""
        pass


    @abstractclassmethod
    def excerpt(self) -> str:
        """Return excerpt of snippet (for preview)."""
        pass


    @abstractclassmethod
    def kind(self) -> str:
        """Return kind of snippet (for filtering)."""
        pass


    def file(self) -> str:
        """Return source file path of snippet"""
        # All nodes should have same source file
        return self.nodes()[0].source


    def scope(self) -> Tuple[int,int]:
        """
        Return the scope of snippet, which corresponding to the line
        number in the source file.

        A scope is a left closed and right open interval of the line number
        ``[left, right)``.
        """
        return self._scope


    def text(self) -> List[str]:
        """Return the original reStructuredText text of snippet."""
        return read_partial_file(self.file(), self.scope())


    def refid(self) -> Optional[str]:
        """
        Return the possible identifier key of snippet.
        It is picked from nodes' (or nodes' parent's) `ids attr`_.

        .. _ids attr: https://docutils.sourceforge.io/docs/ref/doctree.html#ids
        """
        return self._refid


    def __getstate__(self) -> Dict[str,Any]:
        """Implement :py:meth:`pickle.object.__getstate__`."""
        return self.__dict__.copy()


@dataclass
class Headline(Snippet):
    """Documentation title and possible subtitle."""
    title:nodes.title
    subtitle:Optional[nodes.title]

    def nodes(self) -> List[nodes.Node]:
        if not self.subtitle:
            return [self.title]
        return [self.title, self.subtitle]


    def excerpt(self) -> str:
        if not self.subtitle:
            return '<%s>' % self.title.astext()
        return '<%s ~%s~>' % (self.title.astext(), self.subtitle.astext())


    @classmethod
    def kind(cls) -> str:
        return 'd'


    def text(self) -> List[str]:
        """
        Headline represents a reStructuredText document,
        so return the whole source file.
        """
        with open(self.file()) as f:
            return f.read().splitlines()


    def __getstate__(self) -> Dict[str,Any]:
        self.title = self.title.deepcopy()
        if self.subtitle:
            self.subtitle = self.subtitle.deepcopy()
        return super().__getstate__()


@dataclass
class Code(Snippet):
    """A code block with description."""
    description:List[nodes.Body]
    block:nodes.literal_block

    def nodes(self) -> List[nodes.Node]:
        return self.description.copy() + [self.block]


    def excerpt(self) -> str:
        return '/%s/ ' % self.language() + \
            self.description[0].astext().replace('\n', '')


    @classmethod
    def kind(cls) -> str:
        return 'c'


    def language(self) -> str:
        """Return the (programing) language that appears in code."""
        return self.block['language']


    def __getstate__(self) -> Dict[str,Any]:
        self.description = [x.deepcopy() for x in self.description]
        self.block = self.block.deepcopy()
        return super().__getstate__()


def read_partial_file(filename:str, scope:Tuple[int,Optional[int]]) -> List[str]:
    lines = []
    with open(filename, "r") as f:
        start = scope[0] - 1
        stop = scope[1] - 1 if scope[1] else None
        for line in itertools.islice(f, start, stop):
            lines.append(line.strip('\n'))
    return lines


def line_of_start(node:nodes.Node) -> int:
    assert node.line
    if isinstance(node, nodes.title):
        if isinstance(node.parent.parent, nodes.document):
            # Spceial case for Document Title / Subtitle
            return 1
        else:
            # Spceial case for section title
            return node.line - 1
    elif isinstance(node, nodes.section):
        if isinstance(node.parent, nodes.document):
            # Spceial case for top level section
            return 1
        else:
            # Spceial case for section
            return node.line - 1
    return node.line


def line_of_end(node:nodes.Node) -> Optional[int]:
    next_node = node.next_node(descend=False, siblings=True, ascend=True)
    while next_node:
        if next_node.line:
            return line_of_start(next_node)
        next_node = next_node.next_node(
            # Some nodes' line attr is always None, but their children has
            # valid line attr
            descend=True,
            # If node and its children have not valid line attr, try use line
            # of next node
            ascend=True, siblings=True)
    # No line found, return the max line of source file
    if node.source:
        with open(node.source) as f:
            return sum(1 for line in f)
    raise AttributeError('None source attr of node %s' % node)
