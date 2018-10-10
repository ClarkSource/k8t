# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import os
import logging
import click
import ujson

from simple_tools.interaction import confirm

from kinja.values import deep_merge, load_value_file, load_defaults, MERGE_METHODS
from kinja.templates import render_template, find_templates, validate_values
from kinja.variants import load_variant
from kinja.util import touch


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
@click.option('--variant-path', type=click.Path(file_okay=False, exists=True))
@click.option('--environment', default='default', show_default=True)
@click.argument('directory', type=click.Path(dir_okay=True, file_okay=False, exists=True))
def gen(method, yes, value_files, values, variant, variant_path, environment, directory):
    """
    merge order: defaults | variant | value files | values
    """

    template_values = deep_merge(
        load_defaults(directory),
        load_variant(variant, variant_path or os.path.join(directory, 'variants'), environment),
        *(load_value_file(p) for p in value_files),
        dict(values),
        method=method)

    for template in find_templates(directory):
        errors = validate_values(template, template_values)

        if errors and not yes:
            for variable, error in errors.items():
                print('[ERROR] %s: %s' % (variable, error))

            if not confirm('continue?'):
                exit(1)

        print('---')
        print('# Source: %s\n' % template)
        print(render_template(template, template_values, environment))

@root.command()
@click.argument('directory', type=click.Path())
def new(directory):
    try:
        os.makedirs(directory)
    except OSError:
        if not confirm('directory "%s" already exists, go ahead?' % directory):
            exit(1)

    os.makedirs(os.path.join(directory, 'variants'), exist_ok=True)

    touch(os.path.join(directory, 'defaults.yaml'))

#
