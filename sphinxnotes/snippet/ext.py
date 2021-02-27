"""
    sphinxnotes.ext.snippet
    ~~~~~~~~~~~~~~~~~~~~~~~

    Sphinx extension for sphinxnotes.snippet.

    :copyright: Copyright 2021 Shengyu Zhang
    :license: BSD, see LICENSE for details.
"""

from __future__ import annotations
from typing import List, Set, Tuple, TYPE_CHECKING
import re

from docutils import nodes

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment
    from sphinx.config import Config
from sphinx.util import logging

from . import config
from . import Snippet, Headline, Notes
from .picker import pick_doctitle, pick_codes
from .cache import Cache, Item
from .keyword import Extractor
from .utils.titlepath import resolve_fullpath, resolve_docpath


logger = logging.getLogger(__name__)

cache:Cache = None

def extract_keywords(s:Snippet) -> List[Tuple[str,float]]:
    from .keyword import FrequencyExtractor
    extractor:Extractor = FrequencyExtractor()
    # from ..snippet.keyword import TextRankExtractor
    # extractor:Extractor = TextRankExtractor()

    # TODO: Deal with more snippet
    if isinstance(s, Notes):
        ns = s.description
        return extractor.extract('\n'.join(map(lambda x:x.astext(), ns)))
    elif isinstance(s, Headline):
        return extractor.extract('\n'.join(map(lambda x:x.astext(), s.nodes())))
    else:
        pass


def on_config_inited(app:Sphinx, cfg:Config) -> None:
    global cache
    if cfg.snippet_config:
        config.update(cfg.snippet_config)
    cache = Cache(config.cache_dir)

    try:
        cache.load()
    except Exception as e:
        logger.warning("failed to laod cache: %s" % e)


def on_env_get_outdated(app:Sphinx, env:BuildEnvironment, added:Set[str],
                         changed:Set[str], removed:Set[str]) -> List[str]:
    # Remove purged indexes and snippetes from db
    for docname in removed:
        cache.purge_doc(app.config.project, docname)
    return []


def on_doctree_resolved(app:Sphinx, doctree:nodes.document, docname:str) -> None:
    # FIXME:
    if not isinstance(doctree, nodes.document):
        return

    matched = len(app.config.snippet_patterns) == 0
    for pat in app.config.snippet_patterns:
        if re.match(pat, docname):
            matched = True
            break

    if not matched:
        cache.purge_doc(app.config.project, docname)
        return

    # Pick document title from doctree
    doctitle = pick_doctitle(doctree)
    cache.add(Item(project=app.config.project,
                   docname=docname,
                   titlepath=resolve_docpath(app.env, docname),
                   snippet=doctitle,
                   keywords=extract_keywords(doctitle)))

    # Pick code snippet from doctree
    codes = pick_codes(doctree)
    for code in codes:
        cache.add(Item(project=app.config.project,
                       docname=docname,
                       titlepath=resolve_fullpath(app.env, doctree, docname, code.nodes()[0]),
                       snippet=code,
                       keywords=extract_keywords(code)))

def on_builder_finished(app:Sphinx, exception) -> None:
    cache.dump()


def setup(app:Sphinx):
    app.add_config_value('snippet_config', None, '')
    app.add_config_value('snippet_patterns', [], '')

    app.connect('config-inited', on_config_inited)
    app.connect('env-get-outdated', on_env_get_outdated)
    app.connect('doctree-resolved', on_doctree_resolved)
    app.connect('build-finished', on_builder_finished)
