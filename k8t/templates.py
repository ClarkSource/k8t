# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import logging
import os
from typing import Set, Tuple

from jinja2 import meta, nodes

from k8t import config

LOGGER = logging.getLogger(__name__)
PROHIBITED_VARIABLE_NAMES = {
    'namespace',
    'cycler',
    'dict',
    'range',
    'lipsum',
    'joiner'
}


def analyze(template_path: str, values: dict, engine) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    secrets = get_secrets(template_path, engine)
    required_variables = get_variables(template_path, engine)
    defined_variables = set(values.keys())

    LOGGER.debug(
        "defined variables: %s", defined_variables)
    LOGGER.debug("found required variables in template %s: %s",
                 template_path, required_variables)

    undefined_variables = required_variables.difference(defined_variables)
    unused_variables = defined_variables.difference(required_variables)
    invalid_variables = {
        var for var in required_variables if var in PROHIBITED_VARIABLE_NAMES
    }

    return (undefined_variables - invalid_variables), unused_variables, invalid_variables, secrets


def validate(template_path: str, values: dict, engine) -> bool:
    config_ok = True
    undefined, _, invalid, secrets = analyze(template_path, values, engine)

    if undefined:
        LOGGER.error(
            "Undefined variables found: %s", sorted(undefined))

    if invalid:
        LOGGER.error(
            "Invalid variable names found: %s", sorted(invalid))

    if secrets:
        if "secrets" not in config.CONFIG:
            LOGGER.error(
                "No configuration for secrets found: %s", config.CONFIG)
            config_ok = False

    return config_ok and not (invalid or undefined)


def get_variables(template_path: str, engine) -> Set[str]:
    template_source = engine.loader.get_source(engine, os.path.basename(template_path))[
        0
    ]
    abstract_syntax_tree = engine.parse(template_source)

    defaults = {
        filter.node.name

        for filter in abstract_syntax_tree.find_all(nodes.Filter)

        if filter.name == "default"
    }

    return (
        meta.find_undeclared_variables(
            abstract_syntax_tree) - (set(engine.globals.keys()) - PROHIBITED_VARIABLE_NAMES) - defaults
    )


def get_secrets(template_path: str, engine) -> Set[str]:
    template_source = engine.loader.get_source(engine, os.path.basename(template_path))[
        0
    ]
    abstract_syntax_tree = engine.parse(template_source)

    return {
        call.args[0].value

        for call in abstract_syntax_tree.find_all(nodes.Call)

        if call.node.name == "get_secret"
    }
