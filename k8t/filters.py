# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

#
# Copyright © 2020 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import base64
import hashlib
import os
import string
from typing import Any

from k8t import config, secret_providers

try:
    from secrets import choice
except ImportError:
    from random import SystemRandom

    choice = SystemRandom().choice


def random_password(length: int) -> str:
    return "".join(
        choice(string.ascii_lowercase + string.digits) for _ in range(length)
    )


def envvar(key: str, default=None) -> str:
    return os.environ.get(key, default)


def b64encode(value: Any) -> str:
    result = None

    if isinstance(value, str):
        result = base64.b64encode(value.encode()).decode()
    elif isinstance(value, int):
        result = base64.b64encode(str(value).encode()).decode()
    elif isinstance(value, bytes):
        result = base64.b64encode(value).decode()
    else:
        raise TypeError("invalid input: {}".format(value))

    return result


def b64decode(value: Any) -> str:
    result = None

    if isinstance(value, str):
        result = base64.b64decode(value.encode()).decode()
    elif isinstance(value, bytes):
        result = base64.b64decode(value).decode()
    else:
        raise TypeError("invalid input: {}".format(value))

    return result


def hashf(value, method="sha256"):
    try:
        hash_method = getattr(hashlib, method)()
    except AttributeError:
        raise RuntimeError("No such hash method: {}".format(method))

    if isinstance(value, str):
        hash_method.update(value.encode())
    elif isinstance(value, bytes):
        hash_method.update(value)
    else:
        raise TypeError("invalid input: {}".format(value))

    return hash_method.hexdigest()


def get_secret(key: str, length: int = None) -> str:
    provider_name = config.CONFIG.get("secrets", {}).get("provider")

    if not provider_name:
        raise RuntimeError("Secrets provider not configured.")

    provider_name = str(provider_name).lower()
    try:
        provider = getattr(secret_providers, provider_name)
    except AttributeError:
        raise NotImplementedError("secret provider {} does not exist.".format(provider_name))

    return provider(key, length)


def to_bool(value: Any):
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.lower()
    if value in ('yes', 'on', '1', 'true', 1):
        return True
    return False
