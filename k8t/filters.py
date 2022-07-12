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
import re
import string
from typing import Any, Optional

from k8t import config, secret_providers, util

try:
    from secrets import choice
except ImportError:
    from random import SystemRandom

    choice = SystemRandom().choice


def random_password(length: int) -> str:
    return "".join(choice(string.ascii_lowercase + string.digits) for _ in range(length))


def envvar(key: str, default: Any = None) -> str:
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
        raise TypeError(f"invalid input: {value}")

    return result


def b64decode(value: Any) -> str:
    result = None

    if isinstance(value, str):
        result = base64.b64decode(value.encode()).decode()
    elif isinstance(value, bytes):
        result = base64.b64decode(value).decode()
    else:
        raise TypeError(f"invalid input: {value}")

    return result


def hashf(value, method="sha256"):
    try:
        hash_method = getattr(hashlib, method)()
    except AttributeError as no_hash_method:
        raise RuntimeError(f"No such hash method: {method}") from no_hash_method

    if isinstance(value, str):
        hash_method.update(value.encode())
    elif isinstance(value, bytes):
        hash_method.update(value)
    else:
        raise TypeError(f"invalid input: {value}")

    return hash_method.hexdigest()


def get_secret(key: str, length: Optional[int] = None) -> str:
    provider_name = config.CONFIG.get("secrets", {}).get("provider")

    if not provider_name:
        raise RuntimeError("Secrets provider not configured.")

    provider_name = str(provider_name).lower()
    try:
        provider = getattr(secret_providers, provider_name)
    except AttributeError as no_secret_provider:
        raise NotImplementedError(f"secret provider {provider_name} does not exist.") from no_secret_provider

    return provider(key, length)


def to_bool(value: Any) -> Optional[bool]:
    if value is None or isinstance(value, bool):
        return value

    if isinstance(value, str):
        value = value.lower()

    if value in ("yes", "on", "1", "true", 1):
        return True

    return False


def sanitize_label(value: str) -> str:
    """
    source: https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/#syntax-and-character-set

    TODO i'm sure there is a smarter way to do this.
    """

    return re.sub(r"(^[^a-z0-9A-Z]|[^a-z0-9A-Z]$|[^a-z0-9A-Z_.-])", "X", value[:63])


def sanitize_cpu(value: Any) -> str:
    """
    sanitize cpu resource values to millicores.
    """
    return f"{standardize_cpu(value)}m"


def sanitize_memory(value: Any) -> str:
    """
    sanitize memory resource values to megabyte.
    """
    return f"{standardize_memory(value)}M"


def standardize_cpu(value: Any) -> int:
    """
    standardize cpu values to millicores.
    """

    value_millis: int

    str_value = str(value)

    if re.fullmatch(r"^[0-9]+(\.[0-9]+)?$", str_value):
        value_millis = int(float(value) * 1000)
    elif re.fullmatch(r"^[0-9]+m$", str_value):
        value_millis = int(str_value[:-1])
    else:
        raise ValueError(f"invalid cpu value: {value}")

    if value_millis < 1:
        raise ValueError(f"invalud cpu value: {value_millis} is less than 1")

    return value_millis


def standardize_memory(value: Any) -> int:
    """
    standardize memory values to a common notation.

    https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-memory
    """

    value_mb: int

    str_value = str(value)

    if re.fullmatch(r"^[0-9]+([EPTGMk]i?)?$", str_value):
        value_mb = util.memory_to_mb(f"{value}B")
    elif re.fullmatch(r"^[0-9]+m$", str_value):
        value_mb = util.memory_to_mb(f"{int(str_value[:-1]) / 1000}B")
    elif re.fullmatch(r"^[0-9]+e[0-9]+$", str_value):
        value_mb = util.memory_to_mb(f"{float(value)}B")
    else:
        raise ValueError(f"invalid memory value: {value}")

    if value_mb < 1:
        raise ValueError(f"invalid memory value: {value_mb} is less than one MB")

    return value_mb
