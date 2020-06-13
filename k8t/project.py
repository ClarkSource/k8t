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


def check_directory(path: str) -> bool:
    return os.path.exists(os.path.join(path, ".k8t"))


def get_base_dir(root: str, cluster: str, environment: str) -> str:
    base_path = root

    if cluster is not None:
        base_path = os.path.join(base_path, "clusters", cluster)

        if not os.path.isdir(base_path):
            raise RuntimeError("No such cluster: {}".format(cluster))

    if environment is not None:
        base_path = os.path.join(base_path, "environments", environment)

        if not os.path.isdir(base_path):
            raise RuntimeError("No such environment: {}".format(environment))

    return base_path


# pylint: disable=too-many-arguments
def find_files(root: str, cluster: str, environment: str, name: str, file_ok=True, dir_ok=True) -> List[str]:
    def check(path):
        return (file_ok and os.path.isfile(path)) or (dir_ok and os.path.isdir(root_path))

    files: List[str] = []

    root_path = os.path.join(root, name)

    if check(root_path):
        files.append(root_path)

    env_found = environment is None

    if environment is not None:
        file_path = os.path.join(root, "environments", environment, name)

        if check(file_path):
            files.append(file_path)
            env_found = True

    if cluster is not None:
        cluster_path = os.path.join(root, "clusters", cluster)

        if not os.path.isdir(cluster_path):
            raise RuntimeError("no such cluster: {}".format(cluster))

        file_path = os.path.join(cluster_path, name)

        if check(file_path):
            files.append(file_path)

        if environment is not None:
            file_path = os.path.join(
                cluster_path, "environments", environment, name)

            if check(file_path):
                files.append(file_path)
                env_found = True

    if not env_found:
        raise RuntimeError("no such environment: {}".format(environment))

    return files
