# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import base64
import copy
import hashlib
import logging
import os
import string
from functools import reduce
from typing import Any, Dict, List

import yaml
from simple_tools.interaction import confirm

LOGGER = logging.getLogger(__name__)

try:
    from secrets import choice
except ImportError:
    from random import SystemRandom

    choice = SystemRandom().choice


def random_password(length: int) -> str:
    return "".join(
        choice(string.ascii_lowercase + string.digits) for _ in range(length)
    )


# def include_file(name: str):
#     fpath = find_file(name, path, cluster, environment)
#
#     with open(fpath, 'rb') as s:
#         return s.read()


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


def touch(fname: str, mode=0o666, dir_fd=None, **kwargs) -> None:
    if not os.path.exists(fname):
        flags = os.O_CREAT | os.O_APPEND
        with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as filep:
            os.utime(
                filep.fileno() if os.utime in os.supports_fd else fname,
                dir_fd=None if os.supports_fd else dir_fd,
                **kwargs,
            )


def makedirs(path, warn_exists=True):
    if os.path.exists(path) and warn_exists:
        if not confirm("directory {} already exists, go ahead?".format(path)):
            raise RuntimeError("aborting")

    os.makedirs(path, exist_ok=True)


MERGE_METHODS = ["ltr", "rtl", "ask", "crash"]


def merge(d_1: dict, d_2: dict, path=None, method="ltr"):
    d_1 = copy.deepcopy(d_1)

    if path is None:
        path = []

    for key in d_2:
        if key in d_1:
            if isinstance(d_1[key], dict) and isinstance(d_2[key], dict):
                d_1[key] = merge(d_1[key], d_2[key],
                                 path + [str(key)],
                                 method=method)
            elif d_1[key] == d_2[key]:
                pass  # same leaf value
            else:
                if method == "ltr":
                    d_1[key] = d_2[key]
                elif method == "rtl":
                    pass
                elif method == "ask":
                    raise NotImplementedError('Merge method "ask"')
                elif method == "crash":
                    raise Exception("Conflict at %s" %
                                    ".".join(path + [str(key)]))
                else:
                    raise Exception("Invalid merge method: %s" % method)
        else:
            d_1[key] = d_2[key]

    return d_1


def deep_merge(*dicts, method="ltr"):
    LOGGER.debug(
        '"%s" merging %s dicts', method, len(dicts))

    if not dicts:
        return {}

    return reduce(
        lambda a, b: merge(a, b, method=method) if b is not None else a, dicts
    )


def load_yaml(path: str) -> dict:
    LOGGER.debug("loading values file: %s", path)

    with open(path, "r") as stream:
        return yaml.safe_load(stream) or dict()


def envvar(key: str, default=None) -> str:
    return os.environ.get(key, default)


def envvalues() -> Dict:
    prefix: str = 'K8T_VALUE_'
    values: dict = dict()

    for key, value in os.environ.items():
        if key.startswith(prefix):
            values[key.replace(prefix, '', 1).lower()] = value

    return values


def list_files(directory: str, files=False, directories=False) -> List[str]:
    result = []

    for _, dirs, files in os.walk(directory):
        if files:
            result.extend(files)

        if directories:
            result.extend(dirs)

        break

    return result
