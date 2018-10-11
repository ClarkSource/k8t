# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import os
import string

try:
    from secrets import choice
except ImportError:
    from random import SystemRandom

    choice = SystemRandom().choice

from jinja2 import Environment, FileSystemLoader, nodes, Markup, contextfunction

from kinja.variants import get_variant_path
from kinja.util import b64encode, b64decode, hash
from kinja.logger import LOGGER


def find_file(name, path, variant, environment):
    LOGGER.debug('looking for file %s in %s, variant %s and environment %s', name, path, variant, environment)

    if variant and environment:
        if environment:
            fpath = os.path.join(path, 'variants', variant, environment, 'files', name)
            LOGGER.debug('checking path: %s', fpath)

            if os.path.exists(fpath):
                return fpath

        fpath = os.path.join(path, 'variants', variant, 'files', name)
        LOGGER.debug('checking path: %s', fpath)

        if os.path.exists(fpath):
            return fpath

    fpath = os.path.join(path, 'files', name)
    LOGGER.debug('checking path: %s', fpath)

    if os.path.exists(fpath):
        return fpath

    raise RuntimeError('File not found: %s' % name)

def get_environment(path, template_path=None, variant=None, environment=None):
    template_path = template_path if template_path else os.path.join(path, 'templates')

    LOGGER.debug('looking for templates in %s and %s', path, template_path)

    env = Environment(loader=FileSystemLoader([path, template_path]))

    env.filters['b64decode'] = b64decode
    env.filters['b64encode'] = b64encode
    env.filters['hash'] = hash

    def include_file(name):
        fpath = find_file(name, path, variant, environment)

        with open(fpath, 'rb') as s:
            return s.read()

    env.globals['include_raw'] = include_file
    env.globals['include_file'] = include_file

    def random_password(length):
        return ''.join(choice(string.ascii_lowercase + string.digits) for _ in range(length))

    env.globals['random_password'] = random_password

    return env


def find_templates(directory):
    for root, _, files in os.walk(directory):
        for f in files:
            if not f.startswith('.') and f != 'defaults.yaml':
                yield os.path.join(root, f)
        break


def load_template(path, variant=None, environment=None):
    env = get_environment(os.path.dirname(path), variant=variant, environment=environment)

    return env.get_template(os.path.basename(path))


def render_template(path, values, variant, environment):
    template = load_template(path, variant, environment)

    try:
        return template.render(values=values, variant=(variant or 'default'), environment=(environment or 'default'))
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


def find_variables(path, variant=None, environment=None):
    env = get_environment(os.path.dirname(path), variant=variant, environment=environment)

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


def validate_values(path, values, variant=None, environment=None):
    variables = find_variables(path, variant=variant, environment=environment)

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
