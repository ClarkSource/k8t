# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os
import shutil

from simple_tools.interaction import confirm

import k8t

ASSET_DIR = os.path.join(os.path.dirname(k8t.__file__), "assets")


def list_available_templates():
    for _, _, files in os.walk(ASSET_DIR):
        yield from [f.rsplit(".")[0] for f in files]

        break


def new_template(kind, dest):
    source = os.path.join(ASSET_DIR, "{}.yaml.j2".format(kind))

    if not os.path.isfile(source):
        raise RuntimeError(
            "Invalid resource {0}, file does not exist: {1}".format(kind, source))

    if os.path.exists(dest):
        if not confirm("file {} already exists, overwrite?".format(dest)):
            raise RuntimeError("aborting")

    shutil.copyfile(source, dest)


# vim: fenc=utf-8:ts=4:sw=4:expandtab
