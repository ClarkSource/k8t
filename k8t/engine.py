# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os

from jinja2 import Environment, FileSystemLoader
from k8t.clusters import get_cluster_path
from k8t.environments import get_environment_path
from k8t.logger import LOGGER
from k8t.secrets import get_secret
from k8t.util import b64decode, b64encode, hashf, random_password


def build(path: str, cluster: str, environment: str):
    template_paths = find_template_paths(path, cluster, environment)

    LOGGER.debug('building template envionment for %s', template_paths)

    env = Environment(loader=FileSystemLoader(template_paths))

    env.filters['b64decode'] = b64decode
    env.filters['b64encode'] = b64encode
    env.filters['hash'] = hashf

    # env.globals['include_raw'] = include_file
    # env.globals['include_file'] = include_file
    env.globals['random_password'] = random_password
    env.globals['get_secret'] = lambda key: get_secret(
        key, path, cluster, environment)

    return env


def find_template_paths(path: str, cluster: str, environment: str):
    LOGGER.debug("finding template paths in %s for %s on %s",
                 path, cluster, environment)

    template_paths = [os.path.join(path, 'templates')]

    if cluster is not None:
        try:
            cluster_path = get_cluster_path(cluster, path)

            cluster_template_path = os.path.join(cluster_path, 'templates')

            if os.path.exists(cluster_template_path):
                LOGGER.debug('adding %s to template paths',
                             cluster_template_path)
                template_paths.append(cluster_template_path)

            if environment is not None:
                environment_path = get_environment_path(
                    environment, cluster_path)

                environment_template_path = os.path.join(
                    environment_path, 'templates')

                if os.path.exists(environment_template_path):
                    LOGGER.debug('adding %s to template paths',
                                 environment_template_path)
                    template_paths.append(environment_template_path)
        except RuntimeError:
            pass

    LOGGER.debug("found template paths: %s", template_paths)

    return reversed(template_paths)
