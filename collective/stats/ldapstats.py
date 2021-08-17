# -*- coding: utf-8 -*-
from collective.stats import init_stats
from collective.stats import STATS
from datetime import datetime
from ldap.ldapobject import SimpleLDAPObject

original_ldap_call = SimpleLDAPObject._ldap_call


def _ldap_call(self, func, *args, **kwargs):
    if getattr(STATS, 'stats', None) is None:
        init_stats()
    start = datetime.now()
    results = original_ldap_call(self, func, *args, **kwargs)
    STATS.stats['ldap-requests'].append(datetime.now() - start)
    return results


SimpleLDAPObject._ldap_call = _ldap_call
