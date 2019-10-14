# -*- coding: utf-8 -*-
#
# Copyright © 2018 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import os
from typing import Set, Tuple

from jinja2 import meta, nodes
from kinja.logger import LOGGER

PROHIBITED_VARIABLE_NAMES = ['namespace']


def analyze(template_path: str, values: dict, engine) -> Tuple[Set[str], Set[str], Set[str], Set[str]]:
    secrets = get_secrets(template_path, engine)
    required_variables = get_variables(template_path, engine)
    defined_variables = set(values.keys())

    undefined_variables = required_variables.difference(defined_variables)
    unused_variables = defined_variables.difference(required_variables)
    invalid_variables = {
        var for var in required_variables if var in PROHIBITED_VARIABLE_NAMES}

    return undefined_variables, unused_variables, invalid_variables, secrets


def validate(template_path: str, values: dict, engine, config) -> bool:
    config_ok = True
    undefined, _, invalid, secrets = analyze(template_path, values, engine)

    if undefined:
        LOGGER.error("Undefined variables found: %s", sorted(undefined))

    if invalid:
        LOGGER.error("Invalid variable names found: %s", sorted(invalid))

    if secrets:
        if 'secrets' not in config:
            LOGGER.error(f"No configuration for secrets found: {config}")
            config_ok = False

    return config_ok and not (invalid or undefined)


def get_variables(template_path: str, engine) -> Set[str]:
    template_source = engine.loader.get_source(
        engine, os.path.basename(template_path))[0]
    abstract_syntax_tree = engine.parse(template_source)

    defaults = {filter.node.name for filter in abstract_syntax_tree.find_all(
        nodes.Filter) if filter.name == "default"}

    return meta.find_undeclared_variables(abstract_syntax_tree) - set(engine.globals.keys()) - defaults


def get_secrets(template_path: str, engine) -> Set[str]:
    template_source = engine.loader.get_source(
        engine, os.path.basename(template_path))[0]
    abstract_syntax_tree = engine.parse(template_source)

    return {
        call.args[0].value for call in abstract_syntax_tree.find_all(nodes.Call) if call.node.name == "get_secret"
    }
