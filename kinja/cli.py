# -*- coding: utf-8 -*-
#
# Copyright © 2018 Clark Germany GmbH
# Author: Aljosha Friemann <aljosha.friemann@clark.de>

import logging
import os
import sys

import click
import coloredlogs
from kinja.clusters import get_cluster_path, list_clusters, load_cluster
from kinja.engine import build
from kinja.environments import list_environments
from kinja.templates import analyze, validate
from kinja.util import MERGE_METHODS, deep_merge, touch
from kinja.values import load_defaults, load_value_file
from simple_tools.interaction import confirm  # type:ignore


@click.group()
@click.option('-d', '--debug/--no-debug', default=False, show_default=True)
def root(debug):
    coloredlogs.install()
    logging.basicConfig(level=logging.INFO if not debug else logging.DEBUG)
    logging.getLogger('botocore').setLevel(logging.INFO)
    logging.getLogger('urllib3').setLevel(logging.INFO)


@root.command(name='validate')
@click.option('-m', '--method', type=click.Choice(MERGE_METHODS), default='ltr', show_default=True)
@click.option('--cluster', '-c')
@click.option('--environment', '-e')
@click.argument('directory', type=click.Path(dir_okay=True, file_okay=False, exists=True), default=os.getcwd())
def cli_validate(method, cluster, environment, directory):
    engine = build(directory, cluster, environment)

    values = deep_merge(  # pylint: disable=redefined-outer-name
        load_defaults(directory),
        (load_cluster(cluster, directory, environment) if cluster else dict()),
        method=method)

    templates = engine.list_templates()  # pylint: disable=redefined-outer-name
    validated = True

    for template_path in templates:
        undefined, unused, invalid = analyze(template_path, values, engine)

        if not (undefined or unused or invalid):
            continue

        print(f"{template_path}:")

        for var in undefined:
            print(f"undefined variable: {var}")

        for var in invalid:
            print(f"invalid variable: {var}")

        for var in unused:
            print(f"unused variable: {var}")

        validated = False

    sys.exit(1 if validated else 0)


@root.command(name='gen')
@click.option('-m', '--method', type=click.Choice(MERGE_METHODS), default='ltr', show_default=True)
@click.option('--value-file', 'value_files', multiple=True, type=click.Path(dir_okay=False, exists=True))
@click.option('--value', 'cli_values', type=(str, str), multiple=True, metavar='<KEY VALUE>')
@click.option('--cluster', '-c')
@click.option('--environment', '-e')
@click.argument('directory', type=click.Path(dir_okay=True, file_okay=False, exists=True), default=os.getcwd())
def cli_gen(method, value_files, cli_values, cluster, environment, directory):  # pylint: disable=redefined-outer-name,too-many-arguments
    """
    merge order: defaults | cluster | value files | values
    """

    values = deep_merge(  # pylint: disable=redefined-outer-name
        load_defaults(directory),
        (load_cluster(cluster, directory, environment) if cluster else dict()),
        *(load_value_file(p) for p in value_files),
        dict(cli_values),
        method=method)

    engine = build(directory, cluster, environment)

    templates = engine.list_templates()  # pylint: disable=redefined-outer-name
    validated = True

    for template_path in templates:
        if not validate(template_path, values, engine):
            print(f"Failed to validate template {template_path}")

            validated = False

    if not validated:
        sys.exit("Failed to validate all templates")

    for template_path in templates:
        print('---')
        print(f"# Source: {template_path}")
        print(engine.get_template(template_path).render(values))


@root.group()
def new():
    pass


@new.command(name='project')
@click.argument('directory', type=click.Path())
def new_project(directory):
    try:
        os.makedirs(directory)
    except OSError:
        if (os.path.abspath(directory) != os.getcwd()
                and not confirm('directory "%s" already exists, go ahead?' % directory)):
            sys.exit(1)
        os.makedirs(directory, exist_ok=True)

    os.makedirs(os.path.join(directory, 'clusters'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'files'), exist_ok=True)

    touch(os.path.join(directory, 'values.yaml'))


@new.command(name='cluster')
@click.argument('name')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def new_cluster(name, directory):
    cluster_path = os.path.join(directory, 'clusters', name)

    try:
        os.makedirs(cluster_path)
    except OSError:
        if not confirm('directory "%s" already exists, go ahead?' % cluster_path):
            sys.exit(1)
        os.makedirs(cluster_path, exist_ok=True)

    os.makedirs(os.path.join(cluster_path, 'environments'), exist_ok=True)
    os.makedirs(os.path.join(cluster_path, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(cluster_path, 'files'), exist_ok=True)

    touch(os.path.join(cluster_path, 'values.yaml'))


@new.command(name='environment')
@click.argument('name')
@click.argument('cluster')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def new_environment(name, cluster, directory):  # pylint: disable=redefined-outer-name
    cluster_path = get_cluster_path(cluster, directory)
    environment_path = os.path.join(cluster_path, 'environments', name)

    try:
        os.makedirs(environment_path)
    except OSError:
        if not confirm('directory "%s" already exists, go ahead?' % environment_path):
            sys.exit(1)
        os.makedirs(environment_path, exist_ok=True)

    os.makedirs(os.path.join(environment_path, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(environment_path, 'files'), exist_ok=True)

    touch(os.path.join(environment_path, 'values.yaml'))


@root.group()
def get():
    pass


@get.command(name='clusters')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def get_clusters(directory):
    for cluster_path in list_clusters(directory):
        print(cluster_path)


@get.command(name='environments')
@click.argument('cluster')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def get_environments(cluster, directory):  # pylint: disable=redefined-outer-name
    cluster_path = get_cluster_path(cluster, directory)

    for environment_path in list_environments(cluster_path):
        print(environment_path)


@get.command(name='templates')
@click.option('--cluster', '-c')
@click.option('--environment', '-e')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def get_templates(directory, cluster, environment):  # pylint: disable=redefined-outer-name
    for template_path in build(directory, cluster, environment).list_templates():
        print(template_path)


@root.group()
def edit():
    pass


@edit.command(name='config')
@click.option('--cluster', '-c')
@click.option('--environment', '-e')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def edit_config(directory, cluster, environment):  # pylint: disable=redefined-outer-name
    file_path: str

    if cluster is not None:
        if environment is not None:
            file_path = os.path.join(
                directory, 'clusters', cluster, 'environments', environment, 'config.yaml')
        else:
            file_path = os.path.join(
                directory, 'clusters', cluster, 'config.yaml')
    else:
        file_path = os.path.join(directory, 'config.yaml')

    os.system('%s %s' % (os.getenv('EDITOR', 'vim'), file_path))


@edit.command(name='values')
@click.option('--cluster', '-c')
@click.option('--environment', '-e')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def edit_values(directory, cluster, environment):  # pylint: disable=redefined-outer-name
    file_path: str

    if cluster is not None:
        if environment is not None:
            file_path = os.path.join(
                directory, 'clusters', cluster, 'environments', environment, 'values.yaml')
        else:
            file_path = os.path.join(
                directory, 'clusters', cluster, 'values.yaml')
    else:
        file_path = os.path.join(directory, 'values.yaml')

    os.system('%s %s' % (os.getenv('EDITOR', 'vim'), file_path))


def main():
    try:
        root()  # pylint: disable=no-value-for-parameter
    except RuntimeError as exc:
        print(exc)
