# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import logging
from typing import Set, Tuple

import yaml  # pylint: disable=E0401
from jinja2 import Environment, meta, nodes  # pylint: disable=E0401

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


class YamlValidationError(Exception):
    """
    Raised if template is rendered into incorrect yaml
    """


def analyze(template_path: str, values: dict, engine: Environment) -> Tuple[Set[str], Set[str], Set[str], bool]:
    template_source = engine.loader.get_source(engine, template_path)[0]
    abstract_syntax_tree = engine.parse(template_source)

    has_secrets = any(getattr(call.node, "name", None) == "get_secret" for call in abstract_syntax_tree.find_all(nodes.Call))
    required_variables = get_variables(abstract_syntax_tree, engine)

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

    return (undefined_variables - invalid_variables), unused_variables, invalid_variables, has_secrets


def validate(template_path: str, values: dict, engine: Environment) -> bool:
    config_ok = True
    undefined, _, invalid, has_secrets = analyze(template_path, values, engine)

    if undefined:
        LOGGER.error(
            "Undefined variables found: %s", sorted(undefined))

    if invalid:
        LOGGER.error(
            "Invalid variable names found: %s", sorted(invalid))

    if has_secrets:
        if "secrets" not in config.CONFIG:
            LOGGER.error(
                "No configuration for secrets found: %s", config.CONFIG)
            config_ok = False

    return config_ok and not (invalid or undefined)


def get_variables(ast, engine: Environment) -> Set[str]:
    undeclared = meta.find_undeclared_variables(ast)

    defaults = {
        filter.node.name

        for filter in ast.find_all(nodes.Filter)

        if filter.name == "default" and hasattr(filter.node, "name")
    }

    guarded = {
        test.node.name

        for test in ast.find_all(nodes.Test)

        if test.name == 'defined' and hasattr(test.node, "name")
    }

    local = {
        assign.target.name

        for assign in ast.find_all(nodes.Assign)
    }

    return (
        undeclared - (set(engine.globals.keys()) - PROHIBITED_VARIABLE_NAMES) - defaults - guarded - local
    )


def render(template_path: str, values: dict, engine: Environment) -> str:
    output = engine.get_template(template_path).render(values)

    try:
        yaml.safe_load_all(output)
    except (yaml.scanner.ScannerError, yaml.parser.ParserError) as err:
        raise YamlValidationError(err) from err

    return output
