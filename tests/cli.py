# -*- coding: utf-8 -*-
# ISC License
#
# Copyright 2019 FL Fintech E GmbH
#
# Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import os

from click.testing import CliRunner

import boto3
from k8t import __license__, __version__
from k8t.cli import root
from k8t.scaffolding import list_available_templates
from moto import mock_ssm


def test_print_version():
    runner = CliRunner()

    result = runner.invoke(root, ['--version'])
    assert result.exit_code == 0
    assert __version__ in result.output

def test_print_license():
    runner = CliRunner()

    result = runner.invoke(root, ['license'])
    assert result.exit_code == 0
    assert __license__ in result.output

def test_new_project():
    runner = CliRunner()

    with runner.isolated_filesystem():
        result = runner.invoke(root, ['new', 'project', 'test'])
        assert result.exit_code == 0
        assert 'Directory created: test' in result.output
        assert 'File created: test/.k8t' in result.output
        assert 'File created: test/values.yaml' in result.output
        assert 'File created: test/config.yaml' in result.output
        assert os.path.exists('test/.k8t')
        assert os.path.exists('test/values.yaml')
        assert os.path.exists('test/config.yaml')

def test_new_cluster():
    runner = CliRunner()

    with runner.isolated_filesystem():
        open('.k8t', 'w')

        result = runner.invoke(root, ['new', 'cluster', 'cluster-1', '.'])
        assert result.exit_code == 0
        assert 'Directory created: ./clusters/cluster-1' in result.output
        assert 'File created: ./clusters/cluster-1/values.yaml' in result.output
        assert 'File created: ./clusters/cluster-1/config.yaml' in result.output
        assert os.path.exists('./clusters/cluster-1/values.yaml')
        assert os.path.exists('./clusters/cluster-1/config.yaml')

def test_new_environment():
    runner = CliRunner()

    with runner.isolated_filesystem():
        open('.k8t', 'w')

        result = runner.invoke(root, ['new', 'environment', 'staging', '.'])
        assert result.exit_code == 0
        assert 'Directory created: ./environments/staging' in result.output
        assert 'File created: ./environments/staging/values.yaml' in result.output
        assert 'File created: ./environments/staging/config.yaml' in result.output
        assert os.path.exists('./environments/staging/values.yaml')
        assert os.path.exists('./environments/staging/config.yaml')

        os.makedirs('clusters/cluster-1')

        result = runner.invoke(root, ['new', 'environment', '-c', 'cluster-1', 'production', '.'])
        assert result.exit_code == 0
        assert 'Directory created: ./clusters/cluster-1/environments/production' in result.output
        assert 'File created: ./clusters/cluster-1/environments/production/values.yaml' in result.output
        assert 'File created: ./clusters/cluster-1/environments/production/config.yaml' in result.output
        assert os.path.exists('./clusters/cluster-1/environments/production/values.yaml')
        assert os.path.exists('./clusters/cluster-1/environments/production/config.yaml')

def test_new_template():
    template_type = list(list_available_templates())[0]
    runner = CliRunner()

    with runner.isolated_filesystem():
        open('.k8t', 'w')

        result = runner.invoke(root, ['new', 'template', '-n', 'bar', template_type, '.'])
        assert result.exit_code == 0
        assert 'Directory created: ./templates' in result.output
        assert f'Template created: ./templates/bar-{template_type}.yaml.j2' in result.output
        assert os.path.exists(f'./templates/bar-{template_type}.yaml.j2')

        result = runner.invoke(root, ['new', 'template', '-p', 'foo', template_type, '.'])
        assert result.exit_code == 0
        assert f'Template created: ./templates/foo{template_type}.yaml.j2' in result.output
        assert os.path.exists(f'./templates/foo{template_type}.yaml.j2')

        result = runner.invoke(root, ['new', 'template', '-p', 'foo', '-n', 'bar', template_type, '.'])
        assert result.exit_code == 0
        assert f'Template created: ./templates/foobar-{template_type}.yaml.j2' in result.output
        assert os.path.exists(f'./templates/foobar-{template_type}.yaml.j2')

        os.makedirs('environments/staging')

        result = runner.invoke(root, ['new', 'template', '-e', 'staging', template_type, '.'])
        assert result.exit_code == 0
        assert 'Directory created: ./environments/staging/templates' in result.output
        assert f'Template created: ./environments/staging/templates/{template_type}.yaml.j2' in result.output
        assert os.path.exists(f'./environments/staging/templates/{template_type}.yaml.j2')

        os.makedirs('clusters/cluster-1')

        result = runner.invoke(root, ['new', 'template', '-c', 'cluster-1', template_type, '.'])
        assert result.exit_code == 0
        assert 'Directory created: ./clusters/cluster-1/templates' in result.output
        assert f'Template created: ./clusters/cluster-1/templates/{template_type}.yaml.j2' in result.output
        assert os.path.exists(f'./clusters/cluster-1/templates/{template_type}.yaml.j2')

        os.makedirs('clusters/cluster-1/environments/production')

        result = runner.invoke(root, ['new', 'template', '-c', 'cluster-1', '-e', 'production', template_type, '.'])
        assert result.exit_code == 0
        assert 'Directory created: ./clusters/cluster-1/environments/production/templates' in result.output
        assert f'Template created: ./clusters/cluster-1/environments/production/templates/{template_type}.yaml.j2' in result.output
        assert os.path.exists(f'./clusters/cluster-1/environments/production/templates/{template_type}.yaml.j2')

        for template_type in list_available_templates():
            result = runner.invoke(root, ['new', 'template', template_type, '.'])
            assert result.exit_code == 0
            assert f'Template created: ./templates/{template_type}.yaml.j2' in result.output
            assert os.path.exists(f'./templates/{template_type}.yaml.j2')

def test_get_clusters():
    runner = CliRunner()

    result = runner.invoke(root, ['get', 'clusters', 'tests/resources/good'])
    assert result.exit_code == 0
    # TODO: Fix that, should return clusters, not environments
    assert 'cluster-1' in result.output
    assert 'cluster-2' in result.output

def test_get_environments():
    runner = CliRunner()

    result = runner.invoke(root, ['get', 'environments', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'some-env' in result.output
    assert 'common-env' in result.output
    assert 'cluster-specific-env' in result.output

    result = runner.invoke(root, ['get', 'environments', '-c', 'cluster-1', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'some-env' not in result.output
    assert 'common-env' in result.output
    assert 'cluster-specific-env' in result.output

    result = runner.invoke(root, ['get', 'environments', '-c', 'cluster-2', 'tests/resources/good'])
    assert result.exit_code == 0
    assert not result.output

def test_get_templates():
    runner = CliRunner()

    result = runner.invoke(root, ['get', 'templates', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2' in result.output
    assert 'common-env-template.yaml.j2' not in result.output
    assert 'cluster-1-template.yaml.j2' not in result.output
    assert 'cluster-1-env-template.yaml.j2' not in result.output
    assert 'composite-template.yaml.j2' not in result.output

    result = runner.invoke(root, ['get', 'templates', '-e', 'common-env', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2' in result.output
    assert 'common-env-template.yaml.j2' in result.output
    assert 'cluster-1-template.yaml.j2' not in result.output
    assert 'cluster-1-env-template.yaml.j2' not in result.output
    assert 'composite-template.yaml.j2' not in result.output

    result = runner.invoke(root, ['get', 'templates', '-e', 'some-env', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2' in result.output
    assert 'common-env-template.yaml.j2' not in result.output
    assert 'cluster-1-template.yaml.j2' not in result.output
    assert 'cluster-1-env-template.yaml.j2' not in result.output
    assert 'composite-template.yaml.j2' not in result.output

    result = runner.invoke(root, ['get', 'templates', '-c', 'cluster-1', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2' in result.output
    assert 'common-env-template.yaml.j2' not in result.output
    assert 'cluster-1-template.yaml.j2' in result.output
    assert 'cluster-1-env-template.yaml.j2' not in result.output
    assert 'composite-template.yaml.j2' not in result.output

    result = runner.invoke(root, ['get', 'templates', '-c', 'cluster-1', '-e', 'cluster-specific-env', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2' in result.output
    assert 'common-env-template.yaml.j2' not in result.output
    assert 'cluster-1-template.yaml.j2' in result.output
    assert 'cluster-1-env-template.yaml.j2' in result.output
    assert 'composite-template.yaml.j2' not in result.output

    result = runner.invoke(root, ['get', 'templates', '-c', 'cluster-1', '-e', 'common-env', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2' in result.output
    assert 'common-env-template.yaml.j2' in result.output
    assert 'cluster-1-template.yaml.j2' in result.output
    assert 'cluster-1-env-template.yaml.j2' not in result.output
    assert 'composite-template.yaml.j2' not in result.output

    result = runner.invoke(root, ['get', 'templates', '-c', 'cluster-2', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2' in result.output
    assert 'common-env-template.yaml.j2' not in result.output
    assert 'cluster-1-template.yaml.j2' not in result.output
    assert 'cluster-1-env-template.yaml.j2' not in result.output
    assert 'composite-template.yaml.j2' in result.output

def test_validate_successful():
    runner = CliRunner()

    result = runner.invoke(root, ['validate', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2: ✔' in result.output
    assert 'common-env-template.yaml.j2: ✔' not in result.output
    assert 'cluster-1-template.yaml.j2: ✔' not in result.output
    assert 'cluster-1-env-template.yaml.j2: ✔' not in result.output
    assert 'composite-template.yaml.j2: ✔' not in result.output

    result = runner.invoke(root, ['validate', '-e', 'common-env', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2: ✔' in result.output
    assert 'common-env-template.yaml.j2: ✔' in result.output
    assert 'cluster-1-template.yaml.j2: ✔' not in result.output
    assert 'cluster-1-env-template.yaml.j2: ✔' not in result.output
    assert 'composite-template.yaml.j2: ✔' not in result.output

    result = runner.invoke(root, ['validate', '-e', 'some-env', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2: ✔' in result.output
    assert 'common-env-template.yaml.j2: ✔' not in result.output
    assert 'cluster-1-template.yaml.j2: ✔' not in result.output
    assert 'cluster-1-env-template.yaml.j2: ✔' not in result.output
    assert 'composite-template.yaml.j2: ✔' not in result.output

    result = runner.invoke(root, ['validate', '-c', 'cluster-1', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2: ✔' in result.output
    assert 'common-env-template.yaml.j2: ✔' not in result.output
    assert 'cluster-1-template.yaml.j2: ✔' in result.output
    assert 'cluster-1-env-template.yaml.j2: ✔' not in result.output
    assert 'composite-template.yaml.j2: ✔' not in result.output

    result = runner.invoke(root, ['validate', '-c', 'cluster-1', '-e', 'cluster-specific-env', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2: ✔' in result.output
    assert 'common-env-template.yaml.j2: ✔' not in result.output
    assert 'cluster-1-template.yaml.j2: ✔' in result.output
    assert 'cluster-1-env-template.yaml.j2: ✔' in result.output
    assert 'composite-template.yaml.j2: ✔' not in result.output

    result = runner.invoke(root, ['validate', '-c', 'cluster-1', '-e', 'common-env', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2: ✔' in result.output
    assert 'common-env-template.yaml.j2: ✔' in result.output
    assert 'cluster-1-template.yaml.j2: ✔' in result.output
    assert 'cluster-1-env-template.yaml.j2: ✔' not in result.output
    assert 'composite-template.yaml.j2: ✔' not in result.output

    result = runner.invoke(root, ['validate', '-c', 'cluster-2', 'tests/resources/good'])
    assert result.exit_code == 0
    assert 'common-template.yaml.j2: ✔' in result.output
    assert 'common-env-template.yaml.j2: ✔' not in result.output
    assert 'cluster-1-template.yaml.j2: ✔' not in result.output
    assert 'cluster-1-env-template.yaml.j2: ✔' not in result.output
    assert 'composite-template.yaml.j2: ✔' in result.output

def test_validate_with_values():
    runner = CliRunner()

    result = runner.invoke(root, ['validate', 'tests/resources/missing_values'])
    assert result.exit_code # TODO: Should be 1
    assert 'template.yaml.j2: ✗' in result.output
    assert '- undefined variable: test' in result.output

    result = runner.invoke(root, ['validate', '--value', 'test', 'something', 'tests/resources/missing_values'])
    assert result.exit_code == 0
    assert 'template.yaml.j2: ✔' in result.output

    result = runner.invoke(
        root,
        ['validate', '--value-file', 'tests/resources/missing_values/value-file.yaml', 'tests/resources/missing_values']
    )
    assert result.exit_code == 0
    assert 'template.yaml.j2: ✔' in result.output

def test_validate_failure():
    runner = CliRunner()

    result = runner.invoke(root, ['validate', 'tests/resources/bad'])
    # TODO: Fix and uncomment
    # assert 'filter-template.yaml.j2: ✗' in result.output
    # assert 'nested-value-adding-template.yaml.j2: ✗' in result.output
    # assert 'nested-value-template.yaml.j2: ✗' in result.output
    assert 'secret-template.yaml.j2: ✗' in result.output # TODO: Crushes, check file
    assert 'several-template.yaml.j2: ✗' in result.output
    assert 'value-template.yaml.j2: ✗' in result.output
    assert 'composite-template.yaml.j2: ✗' in result.output
    # assert 'invalid-yaml-template.yaml.j2: ✗' in result.output
    # assert 'composite-invalid-yaml-template.yaml.j2: ✗' in result.output

@mock_ssm
def test_gen():
    client = boto3.client('ssm', region_name='eu-central-1')

    client.put_parameter(
        Name="/cluster-1/test",
        Description="Environment specific simple parameter",
        Value="string_value",
        Type="String",
    )

    runner = CliRunner()

    with open('tests/resources/results/default.yaml', 'r') as file:
        result = runner.invoke(root, ['gen', 'tests/resources/good'])
        assert result.exit_code == 0
        assert result.output == file.read()

    with open('tests/resources/results/some-env.yaml', 'r') as file:
        result = runner.invoke(root, ['gen', '-e', 'some-env', 'tests/resources/good'])
        assert result.exit_code == 0
        assert result.output == file.read()

    with open('tests/resources/results/common-env.yaml', 'r') as file:
        result = runner.invoke(root, ['gen', '-e', 'common-env', 'tests/resources/good'])
        assert result.exit_code == 0
        assert result.output == file.read()

    with open('tests/resources/results/cluster-1.yaml', 'r') as file:
        result = runner.invoke(root, ['gen', '-c', 'cluster-1', 'tests/resources/good'])
        assert result.exit_code == 0
        assert result.output == file.read()

    with open('tests/resources/results/cluster-1-common-env.yaml', 'r') as file:
        result = runner.invoke(root, ['gen', '-c', 'cluster-1', '-e', 'common-env', 'tests/resources/good'])
        assert result.exit_code == 0
        assert result.output == file.read()

    with open('tests/resources/results/cluster-1-cluster-specific-env.yaml', 'r') as file:
        result = runner.invoke(root, ['gen', '-c', 'cluster-1', '-e', 'cluster-specific-env', 'tests/resources/good'])
        assert result.exit_code == 0
        assert result.output == file.read()

    with open('tests/resources/results/cluster-2.yaml', 'r') as file:
        result = runner.invoke(root, ['gen', '-c', 'cluster-2', 'tests/resources/good'])
        assert result.exit_code == 0
        assert result.output == file.read()


# vim: fenc=utf-8:ts=4:sw=4:expandtab
