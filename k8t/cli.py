# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import logging
import os
import sys

import click
import coloredlogs
from k8t import __license__, __version__
from k8t.clusters import get_cluster_path, list_clusters, load_cluster
from k8t.config import load_configuration
from k8t.engine import build
from k8t.environments import list_environments
from k8t.templates import analyze, validate
from k8t.util import MERGE_METHODS, deep_merge, touch
from k8t.values import load_defaults, load_value_file
from simple_tools.interaction import confirm
from termcolor import colored


def check_directory(path: str) -> bool:
    return os.path.exists(os.path.join(path, '.k8t'))


@click.group()
@click.version_option(version=__version__)
@click.option('-d', '--debug/--no-debug', default=False, show_default=True, help='Enable debug logging.')
def root(debug):
    coloredlogs.install()
    logging.basicConfig(level=logging.INFO if not debug else logging.DEBUG)
    logging.getLogger('botocore').setLevel(
        logging.WARN if not debug else logging.INFO)
    logging.getLogger('urllib3').setLevel(
        logging.WARN if not debug else logging.INFO)


@root.command(name='license', help='Print software license.')
def print_license():
    print(__license__)


@root.command(name='validate', help='Validate template files for given context.')
@click.option('-m', '--method', type=click.Choice(MERGE_METHODS), default='ltr', show_default=True, help='Value file merge method.')
@click.option('--cluster', '-c', help='Cluster context to use.')
@click.option('--environment', '-e', help='Deployment environment to use.')
@click.argument('directory', type=click.Path(dir_okay=True, file_okay=False, exists=True), default=os.getcwd())
def cli_validate(method, cluster, environment, directory):
    if not check_directory(directory):
        sys.exit(f"not a valid project: {directory}")

    values = deep_merge(  # pylint: disable=redefined-outer-name
        load_defaults(directory),
        (load_cluster(cluster, directory, environment) if cluster else dict()),
        method=method)

    engine = build(directory, cluster, environment)
    config = load_configuration(directory, cluster, environment)

    templates = engine.list_templates()  # pylint: disable=redefined-outer-name

    all_validated = True

    for template_path in templates:
        errors = set()

        undefined, unused, invalid, secrets = analyze(
            template_path, values, engine)

        if undefined or invalid:
            for var in undefined:
                errors.add(f"undefined variable: {var}")

            for var in invalid:
                errors.add(f"invalid variable: {var}")

        if secrets:
            if 'secrets' not in config or 'provider' not in config['secrets']:
                errors.add("No secrets provider configured")

        if errors:
            all_validated = False

            print(
                colored(f"{template_path}: ✗", 'red'))

            for error in errors:
                print(f"- {error}")
        else:
            print(
                colored(f"{template_path}: ✔", 'green'))

    sys.exit(not all_validated)


@root.command(name='gen', help='Create manifest files using stored templates.')
@click.option('-m', '--method', type=click.Choice(MERGE_METHODS), default='ltr', show_default=True, help='Value file merge method.')
@click.option('--value-file', 'value_files', multiple=True, type=click.Path(dir_okay=False, exists=True), help='Additional value file to include.')
@click.option('--value', 'cli_values', type=(str, str), multiple=True, metavar='<KEY VALUE>', help='Additional value(s) to include.')
@click.option('--cluster', '-c', help='Cluster context to use.')
@click.option('--environment', '-e', help='Deployment environment to use.')
@click.argument('directory', type=click.Path(dir_okay=True, file_okay=False, exists=True), default=os.getcwd())
def cli_gen(method, value_files, cli_values, cluster, environment, directory):  # pylint: disable=redefined-outer-name,too-many-arguments
    """
    Merge order: defaults | cluster | value files | values
    """

    if not check_directory(directory):
        sys.exit(f"not a valid project: {directory}")

    values = deep_merge(  # pylint: disable=redefined-outer-name
        load_defaults(directory),
        (load_cluster(cluster, directory, environment) if cluster else dict()),
        *(load_value_file(p) for p in value_files),
        dict(cli_values),
        method=method)

    engine = build(directory, cluster, environment)
    config = load_configuration(directory, cluster, environment)

    templates = engine.list_templates()  # pylint: disable=redefined-outer-name
    validated = True

    for template_path in templates:
        if not validate(template_path, values, engine, config):
            print(f"Failed to validate template {template_path}")

            validated = False

    if not validated:
        sys.exit(1)

    for template_path in templates:
        print('---')
        print(f"# Source: {template_path}")
        print(engine.get_template(template_path).render(values))


@root.group(help='Code scaffolding commands.')
def new():
    pass


@new.command(name='project', help='Create a new project.')
@click.argument('directory', type=click.Path())
def new_project(directory):
    try:
        os.makedirs(directory)
    except OSError:
        if (os.path.abspath(directory) != os.getcwd()
                and not confirm('directory "%s" already exists, go ahead?' % directory)):
            sys.exit(1)
        os.makedirs(directory, exist_ok=True)

    touch(os.path.join(directory, '.k8t'))

    os.makedirs(os.path.join(directory, 'clusters'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(directory, 'files'), exist_ok=True)

    touch(os.path.join(directory, 'values.yaml'))


@new.command(name='cluster', help='Create a new cluster context.')
@click.argument('name')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def new_cluster(name, directory):
    if not check_directory(directory):
        sys.exit(f"not a valid project: {directory}")

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


@new.command(name='environment', help='Create a new environment context.')
@click.argument('cluster')
@click.argument('name')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def new_environment(cluster, name, directory):  # pylint: disable=redefined-outer-name
    if not check_directory(directory):
        sys.exit(f"not a valid project: {directory}")

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


@root.group(help='Project inspection commands.')
def get():
    pass


@get.command(name='clusters', help='Get configured clusters.')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def get_clusters(directory):
    if not check_directory(directory):
        sys.exit(f"not a valid project: {directory}")

    for cluster_path in list_clusters(directory):
        print(cluster_path)


@get.command(name='environments', help='Get configured environments.')
@click.argument('cluster')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def get_environments(cluster, directory):  # pylint: disable=redefined-outer-name
    if not check_directory(directory):
        sys.exit(f"not a valid project: {directory}")

    cluster_path = get_cluster_path(cluster, directory)

    for environment_path in list_environments(cluster_path):
        print(environment_path)


@get.command(name='templates', help='Get stored templates.')
@click.option('--cluster', '-c', help='Cluster context to use.')
@click.option('--environment', '-e', help='Deployment environment to use.')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def get_templates(directory, cluster, environment):  # pylint: disable=redefined-outer-name
    if not check_directory(directory):
        sys.exit(f"not a valid project: {directory}")

    for template_path in build(directory, cluster, environment).list_templates():
        print(template_path)


@root.group(help='Edit local project files.')
def edit():
    pass


@edit.command(name='config', help='Edit config files in chosen context.')
@click.option('--cluster', '-c', help='Cluster context to use.')
@click.option('--environment', '-e', help='Deployment environment to use.')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def edit_config(directory, cluster, environment):  # pylint: disable=redefined-outer-name
    if not check_directory(directory):
        sys.exit(f"not a valid project: {directory}")

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


@edit.command(name='values', help='Edit value files in chosen context.')
@click.option('--cluster', '-c', help='Cluster context to use.')
@click.option('--environment', '-e', help='Deployment environment to use.')
@click.argument('directory', type=click.Path(exists=True, file_okay=False), default=os.getcwd())
def edit_values(directory, cluster, environment):  # pylint: disable=redefined-outer-name
    if not check_directory(directory):
        sys.exit(f"not a valid project: {directory}")

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
        sys.exit(exc)
