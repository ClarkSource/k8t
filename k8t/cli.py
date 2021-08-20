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
from functools import update_wrapper

import click
from jinja2.exceptions import UndefinedError

import coloredlogs
import k8t
from k8t import cluster, config, environment, project, scaffolding, values
from k8t.engine import build
from k8t.templates import YamlValidationError, analyze, render, validate
from k8t.util import (MERGE_METHODS, deep_merge, envvalues, load_cli_value,
                      load_yaml)


def requires_project_directory(func):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        if not project.check_directory(kwargs["directory"]):
            sys.exit("not a valid project: {}".format(kwargs["directory"]))

        return ctx.invoke(func, *args, **kwargs)

    return update_wrapper(new_func, func)


@click.group()
@click.version_option(version=k8t.__version__)
@click.option("-d", "--debug", is_flag=True, default=False, show_default=True, help="Enable debug logging.")
@click.option("-t", "--trace", is_flag=True, default=False, show_default=True, help="Enable spammy logging.")
def root(debug, trace):
    coloredlogs.install(level=logging.DEBUG if debug else logging.INFO)

    if not trace:
        logging.getLogger("botocore").setLevel(
            logging.WARN if not debug else logging.INFO)
        logging.getLogger("urllib3").setLevel(
            logging.WARN if not debug else logging.INFO)


@root.command(name="license", help="Print software license.")
def print_license():
    click.echo(k8t.__license__)

# pylint: disable=too-many-locals,too-many-arguments
@root.command(name="validate", help="Validate template files for given context.")
@click.option("-m", "--method", type=click.Choice(MERGE_METHODS), default="ltr", show_default=True, help="Value file merge method.")
@click.option("--value-file", "value_files", multiple=True, type=click.Path(dir_okay=False, exists=True), help="Additional value file to include.")
@click.option("--value", "cli_values", type=(str, str), multiple=True, metavar="<KEY VALUE>", help="Additional value(s) to include.")
@click.option("--cluster", "-c", "cname", help="Cluster context to use.")
@click.option("--environment", "-e", "ename", help="Deployment environment to use.")
@click.option("--suffix", "-s", "suffixes", default=[".yaml", ".j2", ".jinja2"], help="Filter template files by suffix. Can be used multiple times.", show_default=True)
@click.argument("directory", type=click.Path(dir_okay=True, file_okay=False, exists=True), default=os.getcwd())
@requires_project_directory
def cli_validate(method, value_files, cli_values, cname, ename, suffixes, directory):
    vals = deep_merge(  # pylint: disable=redefined-outer-name
        values.load_all(directory, cname, ename, method),
        *(load_yaml(p) for p in value_files),
        dict(load_cli_value(k, v) for k, v in cli_values),
        envvalues(),
        method=method,
    )
    config.CONFIG = config.load_all(directory, cname, ename, method)

    eng = build(directory, cname, ename)

    templates = eng.list_templates()  # pylint: disable=redefined-outer-name

    if suffixes:
        templates = [ name for name in templates if os.path.splitext(name)[1] in suffixes ]

    all_validated = True

    for template_path in templates:
        errors = set()

        undefined, _, invalid, secrets = analyze(template_path, vals, eng)

        if undefined or invalid:
            for var in undefined:
                errors.add("undefined variable: {}".format(var))

            for var in invalid:
                errors.add("invalid variable: {}".format(var))

        if secrets:
            if "secrets" not in config.CONFIG or "provider" not in config.CONFIG["secrets"]:
                errors.add("No secrets provider configured")

        if errors:
            all_validated = False

            click.secho("{}: ✗".format(template_path), fg="red")

            for error in errors:
                click.echo("- {}".format(error))
        else:
            click.secho("{}: ✔".format(template_path), fg="green")

    sys.exit(not all_validated)


@root.command(name="gen", help="Create manifest files using stored templates.")
@click.option("-m", "--method", type=click.Choice(MERGE_METHODS), default="ltr", show_default=True, help="Value file merge method.")
@click.option("--value-file", "value_files", multiple=True, type=click.Path(dir_okay=False, exists=True), help="Additional value file to include.")
@click.option("--value", "cli_values", type=(str, str), multiple=True, metavar="<KEY VALUE>", help="Additional value(s) to include.")
@click.option("--cluster", "-c", "cname", help="Cluster context to use.")
@click.option("--environment", "-e", "ename", help="Deployment environment to use.")
@click.option("--suffix", "-s", "suffixes", default=[".yaml", ".j2", ".jinja2"], help="Filter template files by suffix. Can be used multiple times.", show_default=True)
@click.option("--secret-provider", help="Secret provider override.")
@click.argument("directory", type=click.Path(dir_okay=True, file_okay=False, exists=True), default=os.getcwd())
@requires_project_directory
def cli_gen(method, value_files, cli_values, cname, ename, suffixes, secret_provider, directory):  # pylint: disable=redefined-outer-name,too-many-arguments
    vals = deep_merge(  # pylint: disable=redefined-outer-name
        values.load_all(directory, cname, ename, method),
        *(load_yaml(p) for p in value_files),
        dict(load_cli_value(k, v) for k, v in cli_values),
        envvalues(),
        method=method,
    )

    config.CONFIG = config.load_all(directory, cname, ename, method)

    if secret_provider is not None:
        if 'secrets' not in config.CONFIG:
            config.CONFIG['secrets'] = dict()

        config.CONFIG['secrets']['provider'] = secret_provider

    eng = build(directory, cname, ename)

    templates = eng.list_templates()  # pylint: disable=redefined-outer-name

    if suffixes:
        templates = [ name for name in templates if os.path.splitext(name)[1] in suffixes ]

    validated = True

    for template_path in templates:
        if not validate(template_path, vals, eng):
            click.echo("Failed to validate template {}".format(template_path))

            validated = False

    if not validated:
        sys.exit(1)

    try:
        for template_path in templates:
            click.echo("---")
            click.echo("# Source: {}".format(template_path))

            template_output = render(template_path, vals, eng)
            click.echo(template_output)
    except (UndefinedError, YamlValidationError) as err:
        click.secho("✗ -> {}".format(err), fg="red")
        sys.exit(1)


@root.group(help="Code scaffolding commands.")
def new():
    pass


@new.command(name="project", help="Create a new project.")
@click.argument("directory", type=click.Path())
def new_project(directory):
    scaffolding.new_project(directory)


@new.command(name="cluster", help="Create a new cluster context.")
@click.argument("name")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), default=os.getcwd())
@requires_project_directory
def new_cluster(name, directory):
    scaffolding.new_cluster(directory, name)


@new.command(name="environment", help="Create a new environment context.")
@click.option("--cluster", "-c", "cname")
@click.argument("name")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), default=os.getcwd())
@requires_project_directory
def new_environment(cname, name, directory):
    base_path = project.get_base_dir(directory, cname, environment=None)

    scaffolding.new_environment(base_path, name)


@new.command(name="template", help="Create specified kubernetes manifest template.")
@click.option("--cluster", "-c", "cname", help="Cluster context to use.")
@click.option("--environment", "-e", "ename", help="Deployment environment to use.")
@click.option("--name", "-n", help="Template filename.")
@click.option("--prefix", "-p", help="Prefix for filename.")
@click.argument("kind", type=click.Choice(sorted(list(scaffolding.list_available_templates()))))
@click.argument("directory", type=click.Path(exists=True, file_okay=False), default=os.getcwd())
@requires_project_directory
def new_template(cname, ename, name, prefix, kind, directory):
    base_path = project.get_base_dir(directory, cname, ename)

    template_name = "{0}{1}{2}{3}.yaml.j2".format(
        prefix or '',
        name or '',
        '-' if name else '',
        kind
    )

    scaffolding.new_template(base_path, template_name, kind)


@root.group(help="Project inspection commands.")
def get():
    pass


@get.command(name="clusters", help="Get configured clusters.")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), default=os.getcwd())
@requires_project_directory
def get_clusters(directory):
    for cluster_path in cluster.list_all(directory):
        click.echo(cluster_path)


@get.command(name="environments", help="Get configured environments.")
@click.option("--cluster", "-c", "cname", help="Cluster context to use.")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), default=os.getcwd())
@requires_project_directory
def get_environments(cname, directory):  # pylint: disable=redefined-outer-name
    path = project.get_base_dir(directory, cname, environment=None)

    for environment_path in environment.list_all(path):
        click.echo(environment_path)


@get.command(name="templates", help="Get stored templates.")
@click.option("--cluster", "-c", "cname", help="Cluster context to use.")
@click.option("--environment", "-e", "ename", help="Deployment environment to use.")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), default=os.getcwd())
@requires_project_directory
def get_templates(directory, cname, ename):  # pylint: disable=redefined-outer-name
    for template_path in build(directory, cname, ename).list_templates():
        click.echo(template_path)


@root.group(help="Edit local project files.")
def edit():
    pass


@edit.command(name="config", help="Edit config files in chosen context.")
@click.option("--cluster", "-c", "cname", help="Cluster context to use.")
@click.option("--environment", "-e", "ename", help="Deployment environment to use.")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), default=os.getcwd())
@requires_project_directory
def edit_config(directory, cname, ename):  # pylint: disable=redefined-outer-name
    file_path: str

    if cname is not None:
        if ename is not None:
            file_path = os.path.join(
                directory, "clusters", cname, "environments", ename, "config.yaml"
            )
        else:
            file_path = os.path.join(
                directory, "clusters", cname, "config.yaml")
    else:
        file_path = os.path.join(directory, "config.yaml")

    click.edit(filename=file_path)


@edit.command(name="values", help="Edit value files in chosen context.")
@click.option("--cluster", "-c", "cname", help="Cluster context to use.")
@click.option("--environment", "-e", "ename", help="Deployment environment to use.")
@click.argument("directory", type=click.Path(exists=True, file_okay=False), default=os.getcwd())
@requires_project_directory
def edit_values(directory, cname, ename):  # pylint: disable=redefined-outer-name
    base_dir = project.get_base_dir(directory, cname, ename)

    file_path = os.path.join(base_dir, "values.yaml")

    click.edit(filename=file_path)


def main():
    try:
        root()  # pylint: disable=no-value-for-parameter
    except RuntimeError as exc:
        sys.exit(exc)
