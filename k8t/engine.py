# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import re
import traceback
import logging

import click

from jinja2 import Environment, FileSystemLoader, Undefined, StrictUndefined

from k8t.filters import (b64decode, b64encode, envvar, get_secret, hashf,
                         random_password, to_bool)
from k8t.project import find_files

LOGGER = logging.getLogger(__name__)

class SilentUndefined(StrictUndefined):
    def __undefined__(self, result = ""):
        stack_summary = traceback.extract_stack()
        for frame_summary in stack_summary:
            file_path = frame_summary.filename
            if re.search(r"\.ya?ml\.j2$", file_path):
                path_parts = file_path.split('/')
                filename = path_parts.pop(-1)

                # TODO: clean up duplication
                env = Environment(loader=FileSystemLoader('/'.join(path_parts)))
                env.filters["b64decode"] = b64decode
                env.filters["b64encode"] = b64encode
                env.filters["hash"] = hashf
                env.filters["bool"] = to_bool

                env.globals["random_password"] = random_password
                env.globals["get_secret"] = get_secret
                env.globals["env"] = envvar
                line_no = env.get_template(filename).get_corresponding_lineno(frame_summary.lineno)
                click.secho("✗ {}:{} - {}".format(file_path, line_no, self._undefined_message), fg="red")

                with open(file_path) as file:
                    for i, line in enumerate(file):
                        if i == line_no - 1:
                            click.secho("> {}".format(line), fg="red")
                            break
        return result

    def stringy(self, *_args):
        return self.__undefined__("")

    def booly(self, *_args):
        return self.__undefined__(False)

    __add__ = __radd__ = __mul__ = __rmul__ = __div__ = __rdiv__ = \
        __truediv__ = __rtruediv__ = __floordiv__ = __rfloordiv__ = \
        __mod__ = __rmod__ = __pos__ = __neg__ = __call__ = \
        __getitem__ = __lt__ = __le__ = __gt__ = __ge__ = __int__ = \
        __float__ = __complex__ = __pow__ = __rpow__ = \
        __iter__ = __str__ = __len__ = __hash__ = \
        stringy
    __eq__ = __ne__ = __bool__ = booly

def build(path: str, cluster: str, environment: str, dry_run: bool = False) -> Environment:
    template_paths = find_template_paths(path, cluster, environment)

    LOGGER.debug(
        "building template environment")

    env = Environment(
        undefined=SilentUndefined if dry_run else Undefined,
        loader=FileSystemLoader(template_paths)
    )

    ### Filter functions ###
    env.filters["b64decode"] = b64decode
    env.filters["b64encode"] = b64encode
    env.filters["hash"] = hashf
    env.filters["bool"] = to_bool

    ### Global functions ###
    # env.globals['include_raw'] = include_file
    # env.globals['include_file'] = include_file
    env.globals["random_password"] = random_password
    env.globals["get_secret"] = get_secret
    env.globals["env"] = envvar

    return env


def find_template_paths(path: str, cluster: str, environment: str):
    LOGGER.debug(
        "finding template paths in %s for cluster=%s on environment=%s", path, cluster, environment
    )

    template_paths = find_files(
        path, cluster, environment, 'templates', file_ok=False)

    LOGGER.debug(
        "found template paths: %s", template_paths)

    return reversed(template_paths)
