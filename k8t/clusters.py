# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

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
