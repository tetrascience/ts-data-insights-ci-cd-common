# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_integration 1'] = [
    {
        'column': 0,
        'endColumn': None,
        'endLine': None,
        'line': 1,
        'message': "Deprecated keyword argument file_category='IDS' passed to Context.write_file()",
        'message-id': 'W1599',
        'module': 'context_deprecation',
        'obj': '',
        'symbol': 'deprecated-context-api',
        'type': 'warning'
    },
    {
        'column': 4,
        'endColumn': None,
        'endLine': None,
        'line': 6,
        'message': "Deprecated keyword argument file_category='IDS' passed to Context.write_file()",
        'message-id': 'W1599',
        'module': 'context_deprecation',
        'obj': 'raw_to_ids',
        'symbol': 'deprecated-context-api',
        'type': 'warning'
    }
]
