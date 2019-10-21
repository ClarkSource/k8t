# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
from typing import Any, Dict

import yaml
from k8t.util import merge


def load_configuration(path: str, cluster: str, environment: str) -> dict:
    config: Dict[str, Any] = dict()

    root_config_path = os.path.join(path, 'config.yaml')

    if os.path.exists(root_config_path):
        config.update(load_config_file(root_config_path))

    if cluster:
        cluster_config_path = os.path.join(
            path, 'clusters', cluster, 'config.yaml')

        if os.path.exists(cluster_config_path):
            config = merge(config, load_config_file(cluster_config_path))

        if environment:
            environment_config_path = os.path.join(
                path, 'clusters', cluster, 'environments', environment, 'config.yaml')

            if os.path.exists(environment_config_path):
                config = merge(config, load_config_file(
                    environment_config_path))

    if not validate(config):
        raise RuntimeError(f"Invalid configuration data: {config}")

    return config


def validate(config: Dict[str, Any]) -> bool:
    if 'secrets' in config:
        assert 'provider' in config['secrets']

    return True


def load_config_file(path: str):
    with open(path, 'rb') as stream:
        return yaml.safe_load(stream.read().decode()) or {}
