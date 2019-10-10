# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import logging
import os

from kinja.logger import LOGGER
from kinja.values import deep_merge, load_value_file


def load_cluster(name: str, path: str, environment: str):
    LOGGER.info('loading cluster from %s with environment %s',
                path, environment)

    cluster_path = get_cluster_path(name, path)

    if not os.path.isdir(cluster_path):
        raise RuntimeError('Invalid cluster path: %s' % cluster_path)

    defaults = dict()
    overrides = dict()

    defaults_path = os.path.join(cluster_path, 'defaults.yaml')

    if os.path.exists(defaults_path):
        defaults = load_value_file(defaults_path)

    if environment:
        environment_path = os.path.join(cluster_path, environment)

        if not os.path.isdir(environment_path):
            raise RuntimeError('Environment not found: %s' % environment)

        overrides_path = os.path.join(environment_path, 'overrides.yaml')

        if os.path.exists(overrides_path):
            overrides = load_value_file(overrides_path)

    return deep_merge(defaults, overrides)


def get_cluster_path(name: str, path: str):
    return os.path.join(path, 'clusters', name)

#
