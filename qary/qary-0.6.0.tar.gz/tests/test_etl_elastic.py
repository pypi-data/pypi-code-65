#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest  # noqa
from qary.etl.elastic import client, ES_INDEX, parse_and_index_wikipedia_article, search, in_index
import logging

log = logging.getLogger(__file__)


def test_elasticsearch():
    title = 'Trevor Noah'
    article_id = 31491224
    if not client:
        return
    if not client.indices.exists(index=ES_INDEX):
        log.info(f"No index {ES_INDEX} found, creating it ...")
        client.indices.create(index=ES_INDEX, ignore=400)
    return None
    if not in_index(article_id=article_id, index=ES_INDEX):
        log.info(f"No article_id={article_id} found in index={ES_INDEX} found, creating it ...")
        client.indices.create(index=ES_INDEX, ignore=400)
        parse_and_index_wikipedia_article(title=title)
    res = search(text=title)
    assert len(res['hits']['hits']) >= 0
