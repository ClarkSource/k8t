# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import os
import base64
import hashlib


def b64encode(s):
    if isinstance(s, str):
        return base64.b64encode(s.encode()).decode()
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
