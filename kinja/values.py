# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import os
import copy
import yaml

from functools import reduce


MERGE_METHODS = ['ltr', 'rtl', 'ask', 'crash']


def merge(a, b, path=None, method='ltr'):
    "merges b into a"
    a = copy.deepcopy(a)
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                a[key] = merge(a[key], b[key], path + [str(key)], method=method)
            elif a[key] == b[key]:
                pass # same leaf value
            else:
                if method == 'ltr':
                    a[key] = b[key]
                elif method == 'rtl':
                    pass
                elif method == 'ask':
                    raise NotImplementedError('Merge method "ask"')
                elif method == 'crash':
                    raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
                else:
                    raise Exception('Invalid merge method: %s' % method)
        else:
            a[key] = b[key]
    return a


def deep_merge(*dicts, method='ltr'):
    return reduce(lambda a, b: merge(a, b, method=method), dicts)


def load_value_file(path):
    with open(path, 'r') as s:
        return yaml.load(s)


def load_defaults(path):
    defaults_path = os.path.join(path, 'defaults.yaml')

    if os.path.exists(defaults_path):
        return load_value_file(defaults_path)

    return dict()

#
