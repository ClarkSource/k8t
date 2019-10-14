# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import os

import yaml
from kinja.logger import LOGGER


def load_value_file(path: str):
    LOGGER.debug('loading values file: %s', path)

    with open(path, 'r') as stream:
        return yaml.safe_load(stream) or dict()


def load_defaults(path: str):
    defaults_path = os.path.join(path, 'values.yaml')

    if os.path.exists(defaults_path):
        return load_value_file(defaults_path)

    return dict()

#
