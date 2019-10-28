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

from k8t.util import makedirs, touch


def list_all(path: str) -> List[str]:
    result: List[str] = []

    for _, dirs, _ in os.walk(os.path.join(path, "environments")):
        result = dirs

        break

    return result


def new(root: str, name: str):
    directory = os.path.join(root, "environments", name)

    makedirs(os.path.join(directory, "templates"))

    touch(os.path.join(directory, "values.yaml"))
    touch(os.path.join(directory, "config.yaml"))


# vim: fenc=utf-8:ts=4:sw=4:expandtab
