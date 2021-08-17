# -*- coding: utf-8 -*-
from collective.stats import init_stats
from collective.stats import STATS
from datetime import datetime
from elasticsearch.transport import Transport

original_perform_request = Transport.perform_request


def perform_request(self, method, url, headers=None, params=None, body=None):
    if getattr(STATS, 'stats', None) is None:
        init_stats()
    start = datetime.now()
    result = original_perform_request(self, method, url, headers, params, body)
    STATS.stats['elasticsearch-requests'].append(datetime.now() - start)
    return result


Transport.perform_request = perform_request
