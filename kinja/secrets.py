# -*- coding: utf-8 -*-
#
# Copyright © 2019 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

from kinja import secret_providers
from kinja.config import load_configuration


def get_secret(key: str, path: str, cluster: str, environment: str) -> str:
    config = load_configuration(path, cluster, environment)

    if 'secrets' not in config:
        raise RuntimeError(f"No configuration for secrets found: {config}")

    provider = getattr(secret_providers, config['secrets']['provider'])

    return provider(f"{config['secrets']['prefix']}/{key}" if 'prefix' in config['secrets'] else key)
