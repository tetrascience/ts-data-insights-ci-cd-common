# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots['test_integration 1'] = [
    {
        'column': 0,
        'endColumn': 36,
        'endLine': 21,
        'line': 21,
        'message': 'Use of deprecated datetime parser',
        'message-id': 'W1598',
        'module': 'datetime_parser_deprecation',
        'obj': '',
        'symbol': 'deprecated-task-script-util-datetime-parser-use',
        'type': 'warning'
    },
    {
        'column': 0,
        'endColumn': 10,
        'endLine': 22,
        'line': 22,
        'message': 'Use of deprecated datetime parser',
        'message-id': 'W1598',
        'module': 'datetime_parser_deprecation',
        'obj': '',
        'symbol': 'deprecated-task-script-util-datetime-parser-use',
        'type': 'warning'
    }
]
