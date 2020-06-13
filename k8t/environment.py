# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
from typing import Set

from k8t.util import list_files


def list_all(path: str) -> Set[str]:
    env_dir = os.path.join(path, 'environments')

    result = set()

    if os.path.isdir(env_dir):
        result.update(list_files(env_dir, include_directories=True))

    cluster_dir = os.path.join(path, 'clusters')

    if os.path.isdir(cluster_dir):
        for cluster in list_files(cluster_dir, include_directories=True):
            result.update(list_all(os.path.join(cluster_dir, cluster)))

    return result


# vim: fenc=utf-8:ts=4:sw=4:expandtab
