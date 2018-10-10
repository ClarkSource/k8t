# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import os
import jinja2schema

from jinja2 import Environment, FileSystemLoader, meta, nodes

from kinja.util import b64encode, b64decode


def get_environment(path):
    env = Environment(loader=FileSystemLoader(path))

    env.filters['b64decode'] = b64decode
    env.filters['b64encode'] = b64encode

    return env


def find_templates(directory):
    for root, _, files in os.walk(directory):
        for f in files:
            if not f.startswith('.') and f != 'defaults.yaml':
                yield os.path.join(root, f)
        break


def load_template(path):
    env = get_environment(os.path.dirname(path))

    return env.get_template(os.path.basename(path))


def render_template(path, values, environment):
    template = load_template(path)

    try:
        return template.render(values=values, environment=environment)
    except TypeError as e:
        raise RuntimeError('missing value')


def merge_node(node):
    """
    Getattr(
        node=Getattr(
            node=Getattr(
                node=Getattr(
                    node=Name(name='values', ctx='load'),
                    attr='rails', ctx='load'),
                attr='insign', ctx='load'),
            attr='sms', ctx='load'),
        attr='password', ctx='load')
    """
    atoms = []
    while isinstance(node, nodes.Getattr):
        atoms.append(node.attr)
        node = node.node
    atoms.append(node.name)

    return '.'.join(list(reversed(atoms)))


def find_variables(path):
    env = get_environment(os.path.dirname(path))

    template_source = env.loader.get_source(env, os.path.basename(path))[0]
    parsed_source = env.parse(template_source)

    variables = set()

    for node in parsed_source.find_all(nodes.Getattr):
        variables.add(merge_node(node))

    return variables


def check_atoms(atoms, values):
    scope = values

    for atom in atoms:
        if atom not in scope:
            raise RuntimeError('Variable "%s" missing from scope: %s' % (atom, scope))

        scope = scope[atom]


def validate_values(path, values):
    variables = find_variables(path)

    errors = dict()

    for variable in variables:
        root, rest = variable.split('.', 1)
        atoms = rest.split('.')

        try:
            check_atoms(atoms, values)
        except RuntimeError as e:
            errors[variable] = e

    return errors

#
