# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import logging
from typing import Any, Dict, List

from k8t.project import find_files
from k8t.util import deep_merge, load_yaml

LOGGER = logging.getLogger(__name__)


def load_all(root: str, cluster: str, environment: str, method: str) -> Dict[str, Any]:
    values: List[str] = find_files(
        root, cluster, environment, "values.yaml", dir_ok=False)

    LOGGER.debug("using value files: %s", values)

    base = dict()

    if cluster is not None:
        base['cluster'] = cluster

    if environment is not None:
        base['environment'] = environment

    return deep_merge(base, *[load_yaml(f) for f in values], method=method)
