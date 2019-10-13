# -*- coding: utf-8 -*-
#
# Copyright © 2019 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import os

from kinja.values import load_value_file


def list_environments(path: str):
    for root, dirs, _ in os.walk(os.path.join(path, 'environments')):
        return [os.path.join(root, dir) for dir in dirs]


def load_environment(name: str, path: str):
    environment_path = get_environment_path(name, path)

    overrides_path = os.path.join(environment_path, 'values.yaml')

    if os.path.exists(overrides_path):
        return load_value_file(overrides_path)


def get_environment_path(name: str, path: str):
    environment_path = os.path.join(path, 'environments', name)

    if not os.path.isdir(environment_path):
        raise RuntimeError('Invalid environment path: %s' % environment_path)

    return environment_path


# vim: fenc=utf-8:ts=4:sw=4:expandtab
