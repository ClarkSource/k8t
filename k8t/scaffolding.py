# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
from typing import List
from k8t.util import makedirs, touch, replace

import k8t

ASSET_DIR = os.path.join(os.path.dirname(k8t.__file__), "assets")


def list_available_templates():
    for _, _, files in os.walk(ASSET_DIR):
        yield from [f.rsplit(".")[0] for f in files]

        break


def new_template(root: str, filename: str, kind: str):
    sourcepath = os.path.join(ASSET_DIR, f"{kind}.yaml.j2")
    if not os.path.isfile(sourcepath):
        raise RuntimeError(f"Invalid resource {kind}, file does not exist: {sourcepath}")

    directory = os.path.join(root, "templates")
    makedirs(directory, warn_exists=False)

    filepath = os.path.join(directory, filename)
    replace(sourcepath, filepath)


def new_project(directory: str):
    _create_scaffold_directory(
        directory=os.path.join(directory),
        files=[".k8t", "values.yaml", "config.yaml"]
    )


def new_cluster(root: str, name: str):
    _create_scaffold_directory(
        directory=os.path.join(root, "clusters", name),
        files=["values.yaml", "config.yaml"]
    )


def new_environment(root: str, name: str):
    _create_scaffold_directory(
        directory=os.path.join(root, "environments", name),
        files=["values.yaml", "config.yaml"]
    )


def _create_scaffold_directory(*, directory: str, files: List[str] = None):
    makedirs(directory)

    if files:
        filepaths = [os.path.join(directory, filename) for filename in files]

        for filepath in filepaths:
            touch(filepath)

# vim: fenc=utf-8:ts=4:sw=4:expandtab
