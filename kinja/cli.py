# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import logging
import os
import sys

import click
from kinja.templates import find_templates, render_template, validate_values
from kinja.util import touch
from kinja.values import (MERGE_METHODS, deep_merge, load_defaults,
                          load_value_file)
from kinja.variants import get_variant_path, load_variant
from simple_tools.interaction import confirm

try:
    import ujson as json
except ImportError:
    import json


@click.group()
@click.option('-d', '--debug/--no-debug', default=False, show_default=True)
@click.pass_context
def root(ctx, debug):
    logging.basicConfig(level=logging.INFO if not debug else logging.DEBUG)


@root.command()
@click.option('-m', '--method', type=click.Choice(MERGE_METHODS), default='ltr', show_default=True)
@click.option('-y', '--yes/--no', default=False)
@click.option('--value-file', 'value_files', multiple=True, type=click.Path(dir_okay=False, exists=True))
@click.option('--value', 'values', type=(str, str), multiple=True, metavar='<KEY VALUE>')
@click.option('--variant')
@click.option('--environment')
@click.argument('directory', type=click.Path(dir_okay=True, file_okay=False, exists=True))
def gen(method, yes, value_files, values, variant, environment, directory):
    """
    merge order: defaults | variant | value files | values
    """

    template_values = deep_merge(
        load_defaults(directory),
        (load_variant(variant, directory, environment) if variant else dict()),
        *(load_value_file(p) for p in value_files),
        dict(values),
        method=method)

    for template in find_templates(directory):
        errors = validate_values(
            template, template_values, variant or 'default', environment)

        if errors and not yes:
            for variable, error in errors.items():
                print('[ERROR] %s: %s' % (variable, error), file=sys.stderr)

            if not confirm('continue?'):
                exit(1)

        render = render_template(
            template, template_values, variant or 'default', environment)

        print('---')
        print('# Source: %s\n' % template)
        print(render)


@root.group()
def new():
    pass


@new.command()
@click.argument('directory', type=click.Path())
def project(directory):
    try:
        os.makedirs(directory)
    except OSError:
        if not confirm('directory "%s" already exists, go ahead?' % directory):
            exit(1)
        os.makedirs(directory, exist_ok=True)

    os.makedirs(os.path.join(directory, 'variants'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'files'), exist_ok=True)

    touch(os.path.join(directory, 'defaults.yaml'))


@new.command()
@click.argument('name')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def variant(name, directory):
    variant_path = os.path.join(directory, 'variants', name)

    try:
        os.makedirs(variant_path)
    except OSError:
        if not confirm('directory "%s" already exists, go ahead?' % variant_path):
            exit(1)
        os.makedirs(variant_path, exist_ok=True)

    os.makedirs(os.path.join(variant_path, 'files'), exist_ok=True)

    touch(os.path.join(variant_path, 'defaults.yaml'))


@new.command()
@click.argument('variant')
@click.argument('name')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def environment(variant, name, directory):
    variant_path = os.path.join(directory, 'variants', variant)

    if not os.path.exists(variant_path):
        exit('No such variant: %s' % variant)

    environment_path = os.path.join(variant_path, name)

    try:
        os.makedirs(environment_path)
    except OSError:
        if not confirm('directory "%s" already exists, go ahead?' % environment_path):
            exit(1)
        os.makedirs(environment_path, exist_ok=True)

    os.makedirs(os.path.join(environment_path, 'files'), exist_ok=True)

    touch(os.path.join(environment_path, 'overrides.yaml'))

#
