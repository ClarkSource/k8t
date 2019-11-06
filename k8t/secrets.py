# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from k8t import secret_providers
from k8t.config import load_all


def get_secret(key: str, path: str, cluster: str, environment: str) -> str:
    config = load_all(path, cluster, environment, 'ltr')

    if "secrets" not in config:
        raise RuntimeError(
            "No configuration for secrets found: {}".format(config))

    provider = getattr(secret_providers, config["secrets"]["provider"].lower())

    return provider(
        "{0}/{1}".format(config['secrets']['prefix'],
                         key) if "prefix" in config["secrets"] else key
    )
