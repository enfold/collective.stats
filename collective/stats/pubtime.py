from collective.stats import STATS
from collective.stats import init_stats
from collective.stats import process
from datetime import datetime
from datetime import timedelta
from zope import component
import ZPublisher.interfaces
import logging
import os

logger = logging.getLogger('collective.stats')


@component.adapter(ZPublisher.interfaces.IPubStart)
def pubStartHandler(ev):
    init_stats()


@component.adapter(ZPublisher.interfaces.IPubAfterTraversal)
def pubAfterTraverseHandler(ev):
    if getattr(STATS, 'stats', None) is None:
        init_stats()
    STATS.stats['time-after-traverse'] = datetime.now() - STATS.stats['time-start']  # noqa


@component.adapter(ZPublisher.interfaces.IPubBeforeCommit)
def pubBeforeCommitHandler(ev):
    if getattr(STATS, 'stats', None) is None:
        init_stats()
    STATS.stats['time-before-commit'] = datetime.now() - STATS.stats['time-start']  # noqa

    try:
        ob = ev.request['PARENTS'][-1]
        conn = ob._p_jar
        STATS.stats['modified'] = len(conn._registered_objects)
    except:
        pass


@component.adapter(ZPublisher.interfaces.IPubSuccess)
def pubSucessHandler(ev):
    environ = ev.request.environ
    if getattr(STATS, 'stats', None) is None:
        init_stats()
    stats = STATS.stats
    stats['time-end'] = datetime.now() - stats['time-start']

    total = 0
    total_cached = 0
    t_total = timedelta()
    t_cached = timedelta()
    t_uncached = timedelta()

    for td in stats['zodb-cached']:
        total += 1
        total_cached += 1
        t_total = t_total + td
        t_cached = t_cached + td

    for td in stats['zodb-uncached']:
        total += 1
        t_total = t_total + td
        t_uncached = t_uncached + td

    loads = timedelta()
    for td in stats['zodb-loads']:
        loads = loads + td

    def printTD(td):
        s = td.seconds + td.microseconds / 1000000.0
        return '%2.4f' % s

    rss1 = stats['memory'][0] / 1024
    rss2 = process.memory_info()[0] / 1024

    ldap_requests = len(stats['ldap-requests'])
    ldap_requests_time = timedelta()
    for td in stats['ldap-requests']:
        ldap_requests_time += td

    elasticsearch_requests = len(stats['elasticsearch-requests'])
    elasticsearch_requests_time = timedelta()
    for td in stats['elasticsearch-requests']:
        elasticsearch_requests_time += td

    redis_requests = len(stats['redis-requests'])
    redis_requests_time = timedelta()
    for td in stats['redis-requests']:
        redis_requests_time += td

    info = (
        printTD(stats['time-end']),
        printTD(stats['time-after-traverse']),
        printTD(stats['time-before-commit']),
        printTD(stats['transchain']),
        printTD(loads),
        total,
        total_cached,
        stats['modified'],
        environ['REQUEST_METHOD'],
        environ['PATH_INFO'],
        printTD(t_total),
        printTD(t_cached),
        printTD(t_uncached),
        rss1,
        rss2,
        ldap_requests,
        printTD(ldap_requests_time),
        elasticsearch_requests,
        printTD(elasticsearch_requests_time),
        redis_requests,
        printTD(redis_requests_time),
    )

    if os.getenv("COLLECTIVE_STATS_DISABLE_LOG") != "1":
        logger.info(
            '| %s %s %s %s %s %0.4d %0.4d %0.4d '
            '| %s:%s | t: %s, t_c: %s, t_nc: %s '
            '| RSS: %s - %s '
            '| %0.4d %s '
            '| %0.4d %s ' 
            '| %0.4d %s' % info
        )

    header_values = info[:8] + info[15:]
    ev.request.response.setHeader(
        'x-stats', '%s %s %s %s %s %0.4d %0.4d %0.4d %0.4d %s %0.4d %s %0.4d %s' % header_values
    )

    del STATS.stats
