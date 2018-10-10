# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import os

from kinja.values import deep_merge, load_value_file, MERGE_METHODS


def load_variant(name, path, environment):
    variant_path = path if not name else os.path.join(path, name)

    if not os.path.isdir(variant_path):
        raise RuntimeError('Invalid variant path: %s' % variant_path)

    values_path = os.path.join(variant_path, '%s.yaml' % environment)

    if not os.path.exists(values_path) or os.path.isdir(values_path):
        raise RuntimeError('No values file found: %s' % values_path)

    return load_value_file(values_path)

#
