# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import os
import logging

from kinja.values import deep_merge, load_value_file
from kinja.logger import LOGGER


def load_variant(name: str, path: str, environment: str):
    LOGGER.info('loading variant from %s with environment %s', path, environment)

    variant_path = get_variant_path(name, path)

    if not os.path.isdir(variant_path):
        raise RuntimeError('Invalid variant path: %s' % variant_path)

    defaults  = dict()
    overrides = dict()

    defaults_path = os.path.join(variant_path, 'defaults.yaml')

    if os.path.exists(defaults_path):
        defaults = load_value_file(defaults_path)

    if environment:
        environment_path = os.path.join(variant_path, environment)

        if not os.path.isdir(environment_path):
            raise RuntimeError('Environment not found: %s' % environment)

        overrides_path = os.path.join(environment_path, 'overrides.yaml')

        if os.path.exists(overrides_path):
            overrides = load_value_file(overrides_path)

    return deep_merge(defaults, overrides)


def get_variant_path(name: str, path: str):
    return os.path.join(path, 'variants', name)

#
