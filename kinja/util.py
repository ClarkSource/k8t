# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import base64


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
