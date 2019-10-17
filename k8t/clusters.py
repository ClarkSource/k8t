# -*- coding: utf-8 -*-
#
# Copyright © 2018 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import os
from typing import Any, Dict, List

from k8t.environments import load_environment
from k8t.logger import LOGGER
from k8t.util import deep_merge
from k8t.values import load_value_file


def list_clusters(path: str) -> List[str]:
    result: List[str] = []

    for root, dirs, _ in os.walk(os.path.join(path, 'clusters')):
        result = dirs

        break

    return result


def load_cluster(name: str, path: str, environment: str):
    LOGGER.debug('loading cluster from %s with environment %s',
                 path, environment)

    cluster_path = get_cluster_path(name, path)

    defaults: Dict[str, Any] = dict()
    overrides: Dict[str, Any] = dict()

    defaults_path = os.path.join(cluster_path, 'values.yaml')

    if os.path.exists(defaults_path):
        defaults = load_value_file(defaults_path)

    if environment:
        overrides = load_environment(environment, cluster_path)

    return deep_merge(defaults, overrides)


def get_cluster_path(name: str, path: str):
    cluster_path = os.path.join(path, 'clusters', name)

    if not os.path.isdir(cluster_path):
        raise RuntimeError('Invalid cluster path: %s' % cluster_path)

    return cluster_path

#
