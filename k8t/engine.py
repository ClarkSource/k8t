# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import logging

from typing import List
from jinja2 import Environment, DictLoader, FileSystemLoader, StrictUndefined

from k8t.filters import (b64decode, b64encode, envvar, get_secret, hashf,
                         random_password, sanitize_label, sanitize_cpu, sanitize_memory, standardize_cpu, standardize_memory, to_bool)
from k8t.project import find_files
from k8t.util import read_file

LOGGER = logging.getLogger(__name__)


def build(path: str, cluster: str, environment: str, template_overrides: List[str] = None) -> Environment:
    env = None
    template_paths = []

    LOGGER.debug(
        "building template environment")

    if template_overrides is not None and len(template_overrides) > 0:
        template_paths = {key: read_file(os.path.abspath(path)) for key, path in template_overrides}

        env = Environment(undefined=StrictUndefined, loader=DictLoader(template_paths))
    else:
        template_paths = find_template_paths(path, cluster, environment)

        env = Environment(undefined=StrictUndefined, loader=FileSystemLoader(template_paths))

    # Filter functions
    env.filters["b64decode"] = b64decode
    env.filters["b64encode"] = b64encode
    env.filters["hash"] = hashf
    env.filters["bool"] = to_bool
    env.filters["sanitize_label"] = sanitize_label
    env.filters["sanitize_cpu"] = sanitize_cpu
    env.filters["sanitize_memory"] = sanitize_memory
    env.filters["standardize_cpu"] = standardize_cpu
    env.filters["standardize_memory"] = standardize_memory

    # Global functions
    env.globals["random_password"] = random_password
    env.globals["get_secret"] = get_secret
    env.globals["env"] = envvar

    # Disabled
    # env.globals['include_raw'] = include_file
    # env.globals['include_file'] = include_file

    return env


def find_template_paths(path: str, cluster: str, environment: str):
    LOGGER.debug(
        "finding template paths in %s for cluster=%s on environment=%s", path, cluster, environment
    )

    template_paths = find_files(
        path, cluster, environment, 'templates', file_ok=False)

    LOGGER.debug(
        "found template paths: %s", template_paths)

    return reversed(template_paths)
