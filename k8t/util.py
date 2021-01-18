# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import copy
import json
import logging
import os
import shutil
from functools import reduce
from typing import Any, Dict, List, Tuple

import yaml  # pylint: disable=E0401
from click import secho  # pylint: disable=E0401

from simple_tools.interaction import confirm  # pylint: disable=E0401

LOGGER = logging.getLogger(__name__)


def touch(fname: str, mode=0o666, dir_fd=None, **kwargs) -> None:
    if os.path.exists(fname):
        secho(f"File exists: {fname}", fg="yellow")
    else:
        flags = os.O_CREAT | os.O_APPEND
        with os.fdopen(os.open(fname, flags=flags, mode=mode, dir_fd=dir_fd)) as filep:
            os.utime(
                filep.fileno() if os.utime in os.supports_fd else fname,
                dir_fd=None if os.supports_fd else dir_fd,
                **kwargs,
            )
        secho(f"File created: {fname}", fg="green")


def makedirs(path, warn_exists=True):
    if os.path.exists(path):
        if warn_exists:
            if confirm("directory {} already exists, go ahead?".format(path)):
                secho(f"Directory exists: {path}", fg="yellow")

                return
            raise RuntimeError("aborting")
        secho(f"Directory exists: {path}", fg="yellow")
    else:
        os.makedirs(path, exist_ok=True)
        secho(f"Directory created: {path}", fg="green")


def replace(source: str, dest: str):
    if os.path.exists(dest):
        if not confirm(f"file {dest} already exists, overwrite?"):
            raise RuntimeError("aborting")

    shutil.copyfile(source, dest)
    secho(f"Template created: {dest}", fg="green")


MERGE_METHODS = ["ltr", "rtl", "ask", "crash"]


def merge(d_1: dict, d_2: dict, path=None, method="ltr"):
    d_1 = copy.deepcopy(d_1)

    if path is None:
        path = []

    for key in d_2:
        if key in d_1:
            if isinstance(d_1[key], dict) and isinstance(d_2[key], dict):
                d_1[key] = merge(d_1[key], d_2[key], path + [str(key)], method=method)
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
                    raise Exception("Conflict at %s" % ".".join(path + [str(key)]))
                else:
                    raise Exception("Invalid merge method: %s" % method)
        else:
            d_1[key] = d_2[key]

    return d_1


def deep_merge(*dicts, method="ltr"):
    LOGGER.debug('"%s" merging %s dicts', method, len(dicts))

    if not dicts:
        return {}

    return reduce(
        lambda a, b: merge(a, b, method=method) if b is not None else a, dicts
    )


def load_yaml(path: str) -> dict:
    LOGGER.debug("loading values file: %s", path)

    with open(path, "r") as stream:
        return yaml.safe_load(stream) or dict()


def load_cli_value(key: str, value: str) -> Tuple[str, Any]:
    LOGGER.debug("loading cli value (%s, %s)", key, value)

    try:
        return key, json.loads(value, parse_float=lambda x: str(x))  # lambda is necessary, pylint: disable=W0108
    except json.decoder.JSONDecodeError:
        return key, value


def envvalues() -> Dict:
    prefix: str = "K8T_VALUE_"
    values: dict = dict()

    for key, value in os.environ.items():
        if key.startswith(prefix):
            values[key.replace(prefix, "", 1).lower()] = value

    return values


def list_files(
    directory: str, include_files=False, include_directories=False
) -> List[str]:
    result = []

    for _, dirs, files in os.walk(directory):
        if include_files:
            result.extend(files)

        if include_directories:
            result.extend(dirs)

        break

    return result
