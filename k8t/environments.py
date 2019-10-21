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

from k8t.values import load_value_file


def list_environments(path: str) -> List[str]:
    result: List[str] = []

    for root, dirs, _ in os.walk(os.path.join(path, 'environments')):
        result = dirs

        break

    return result


def load_environment(name: str, path: str) -> Dict[str, Any]:
    environment_path = get_environment_path(name, path)

    overrides_path = os.path.join(environment_path, 'values.yaml')

    if os.path.exists(overrides_path):
        return load_value_file(overrides_path)

    return dict()


def get_environment_path(name: str, path: str) -> str:
    environment_path = os.path.join(path, 'environments', name)

    if not os.path.isdir(environment_path):
        raise RuntimeError('Invalid environment path: %s' % environment_path)

    return environment_path


# vim: fenc=utf-8:ts=4:sw=4:expandtab
