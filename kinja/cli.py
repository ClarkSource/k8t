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


@click.command()
@click.option('-d', '--debug/--no-debug', default=False, show_default=True)
@click.option('-m', '--method', type=click.Choice(MERGE_METHODS), default='ltr', show_default=True)
@click.option('-v', '--values', 'value_files', multiple=True, type=click.Path(dir_okay=False))
@click.option('--value', 'values', type=(str, str), multiple=True, metavar='<KEY VALUE>')
@click.option('--variant')
@click.option('--variant-path', type=click.Path(file_okay=False))
@click.option('--environment', default='default', show_default=True)
@click.argument('directory', type=click.Path(dir_okay=True, file_okay=False))
def root(debug, method, value_files, values, variant, variant_path, environment, directory):
    """
    merge order: defaults | variant | value files | values
    """
    logging.basicConfig(level=logging.INFO if not debug else logging.DEBUG)

    template_values = deep_merge(
        load_defaults(variant_path or directory),
        load_variant(variant, variant_path or os.path.join(directory, 'variants'), environment),
        *(load_value_file(p) for p in value_files),
        dict(values),
        method=method)

    for template in find_templates(directory):
        errors = validate_values(template, template_values)

        if errors:
            for variable, error in errors.items():
                print('[ERROR] %s: %s' % (variable, error))

            if not confirm('continue?'):
                exit(1)

        print(render_template(template, template_values))
