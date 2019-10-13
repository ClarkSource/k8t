# -*- coding: utf-8 -*-
#
# Copyright © 2018 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import base64
import copy
import hashlib
import os
import string
from functools import reduce

from kinja.logger import LOGGER

try:
    from secrets import choice
except ImportError:
    from random import SystemRandom

    choice = SystemRandom().choice


def random_password(length: int) -> str:
    return ''.join(choice(string.ascii_lowercase + string.digits) for _ in range(length))


# def include_file(name: str):
#     fpath = find_file(name, path, cluster, environment)
#
#     with open(fpath, 'rb') as s:
#         return s.read()


def b64encode(s):
    if isinstance(s, str):
        return base64.b64encode(s.encode()).decode()
    elif isinstance(s, int):
        return base64.b64encode(str(s).encode()).decode()
    elif isinstance(s, bytes):
        return base64.b64encode(s).decode()
    else:
        raise TypeError('invalid input: %s' % s)


def b64decode(s):
    if isinstance(s, str):
        return base64.b64decode(s.encode()).decode()
    elif isinstance(s, bytes):
        return base64.b64decode(s).decode()
    else:
        raise TypeError('invalid input: %s' % s)


def hash(s, method='sha256'):
    try:
        h = getattr(hashlib, method)()
    except AttributeError:
        raise RuntimeError('No such hash method: %s' % method)

    if isinstance(s, str):
        h.update(s.encode())
    elif isinstance(s, bytes):
        h.update(s)
    else:
        raise TypeError('invalid input: %s' % s)

    return h.hexdigest()


def touch(fname, mode=0o666, dir_fd=None, **kwargs):
    flags = os.O_CREAT | os.O_APPEND
    with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as f:
        os.utime(f.fileno() if os.utime in os.supports_fd else fname,
            dir_fd=None if os.supports_fd else dir_fd, **kwargs)


MERGE_METHODS = ['ltr', 'rtl', 'ask', 'crash']


def merge(a: dict, b: dict, path=None, method='ltr'):
    a = copy.deepcopy(a)

    if path is None:
        path = []

    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                a[key] = merge(a[key], b[key], path +
                               [str(key)], method=method)
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                if method == 'ltr':
                    a[key] = b[key]
                elif method == 'rtl':
                    pass
                elif method == 'ask':
                    raise NotImplementedError('Merge method "ask"')
                elif method == 'crash':
                    raise Exception('Conflict at %s' %
                                    '.'.join(path + [str(key)]))
                else:
                    raise Exception('Invalid merge method: %s' % method)
        else:
            a[key] = b[key]

    return a


def deep_merge(*dicts, method='ltr'):
    LOGGER.debug('"%s" merging %s dicts', method, len(dicts))

    return reduce(lambda a, b: merge(a, b, method=method) if b is not None else a, dicts)
