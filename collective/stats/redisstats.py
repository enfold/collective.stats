# -*- coding: utf-8 -*-
from collective.stats import init_stats
from collective.stats import STATS
from datetime import datetime
from redis.connection import Connection

original_send_packed_command = Connection.send_packed_command


def send_packed_command(self, command, check_health=True):
    if getattr(STATS, 'stats', None) is None:
        init_stats()
    start = datetime.now()
    original_send_packed_command(self, command, check_health)
    STATS.stats['redis-requests'].append(datetime.now() - start)


Connection.send_packed_command = send_packed_command
