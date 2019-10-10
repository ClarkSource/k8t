# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2018 Clark Germany GmbH

import logging
import os
import sys

import click
from kinja.clusters import get_cluster_path, load_cluster
from kinja.templates import find_templates, render_template, validate_values
from kinja.util import touch
from kinja.values import (MERGE_METHODS, deep_merge, load_defaults,
                          load_value_file)
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
@click.option('--cluster')
@click.option('--environment')
@click.argument('directory', type=click.Path(dir_okay=True, file_okay=False, exists=True))
def gen(method, yes, value_files, values, cluster, environment, directory):
    """
    merge order: defaults | cluster | value files | values
    """

    template_values = deep_merge(
        load_defaults(directory),
        (load_cluster(cluster, directory, environment) if cluster else dict()),
        *(load_value_file(p) for p in value_files),
        dict(values),
        method=method)

    for template in find_templates(directory):
        errors = validate_values(
            template, template_values, cluster or 'default', environment)

        if errors and not yes:
            for variable, error in errors.items():
                print('[ERROR] %s: %s' % (variable, error), file=sys.stderr)

            if not confirm('continue?'):
                exit(1)

        render = render_template(
            template, template_values, cluster or 'default', environment)

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

    os.makedirs(os.path.join(directory, 'clusters'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'files'), exist_ok=True)

    touch(os.path.join(directory, 'defaults.yaml'))


@new.command()
@click.argument('name')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def cluster(name, directory):
    cluster_path = os.path.join(directory, 'clusters', name)

    try:
        os.makedirs(cluster_path)
    except OSError:
        if not confirm('directory "%s" already exists, go ahead?' % cluster_path):
            exit(1)
        os.makedirs(cluster_path, exist_ok=True)

    os.makedirs(os.path.join(cluster_path, 'files'), exist_ok=True)

    touch(os.path.join(cluster_path, 'defaults.yaml'))


@new.command()
@click.argument('cluster')
@click.argument('name')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def environment(cluster, name, directory):
    cluster_path = os.path.join(directory, 'clusters', cluster)

    if not os.path.exists(cluster_path):
        exit('No such cluster: %s' % cluster)

    environment_path = os.path.join(cluster_path, name)

    try:
        os.makedirs(environment_path)
    except OSError:
        if not confirm('directory "%s" already exists, go ahead?' % environment_path):
            exit(1)
        os.makedirs(environment_path, exist_ok=True)

    os.makedirs(os.path.join(environment_path, 'files'), exist_ok=True)

    touch(os.path.join(environment_path, 'overrides.yaml'))

#
