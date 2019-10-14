# -*- coding: utf-8 -*-
#
# Copyright © 2019 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import os
from typing import Any, Dict

import yaml
from kinja.util import merge


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
