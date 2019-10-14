# -*- coding: utf-8 -*-
#
# Copyright © 2018 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import os
from typing import Set, Tuple

from jinja2 import meta
from kinja.logger import LOGGER

PROHIBITED_VARIABLE_NAMES = ['namespace']


def analyze(template_path: str, values: dict, engine) -> Tuple[Set[str], Set[str], Set[str]]:
    required_variables = get_variables(template_path, engine)
    defined_variables = set(values.keys())

    undefined_variables = required_variables.difference(defined_variables)
    unused_variables = defined_variables.difference(required_variables)
    invalid_variables = {
        var for var in required_variables if var in PROHIBITED_VARIABLE_NAMES}

    return undefined_variables, unused_variables, invalid_variables


def validate(template_path: str, values: dict, engine) -> bool:
    undefined, _, invalid = analyze(template_path, values, engine)

    if undefined:
        LOGGER.error("Undefined variables found: %s", sorted(undefined))

    if invalid:
        LOGGER.error("Invalid variable names found: %s", sorted(invalid))

    return not (invalid or undefined)


def get_variables(template_path: str, engine) -> Set[str]:
    template_source = engine.loader.get_source(
        engine, os.path.basename(template_path))[0]
    abstract_syntax_tree = engine.parse(template_source)

    return meta.find_undeclared_variables(abstract_syntax_tree) - set(engine.globals.keys())
