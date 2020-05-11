# k8t

*Pronounced katie [ˈkeɪti]*

[![Build Status](https://jenkins.ci.flfinteche.de/buildStatus/icon?job=DevOps%2Fk8t%2Fmaster)](https://jenkins.ci.flfinteche.de/job/DevOps/job/k8t/job/master/)
[![PyPi version](https://pypip.in/v/k8t/badge.png)](https://pypi.org/project/k8t/)
[![PyPi downloads](https://pypip.in/d/k8t/badge.png)](https://pypi.org/project/k8t/)
[![CLARK Open Source](https://img.shields.io/badge/CLARK-Open%20Source-%232B6CDE.svg)](https://www.clark.de/de/jobs)

Simple cluster and environment specific aware templating for kubernetes manifests.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Installation](#installation)
  - [Completion](#completion)
- [Concepts](#concepts)
  - [*Clusters* and *Environments*](#clusters-and-environments)
  - [Templating](#templating)
    - [Template helper functions](#template-helper-functions)
- [Usage](#usage)
  - [Scaffolding](#scaffolding)
  - [Config management](#config-management)
  - [Validate templates](#validate-templates)
  - [Generate manifests](#generate-manifests)
  - [Overriding templates](#overriding-templates)
  - [Managing secrets](#managing-secrets)
    - [Providers](#providers)
      - [SSM](#ssm)
      - [Random](#random)
- [TODO](#todo)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Installation

run this

```bash
$ pip install --user --upgrade k8t
```

**note**: k8t is not Python 2 compatible

### Completion

Run the following and store the file in your distribution/OS specific spot

bash:

```bash
$ _K8T_COMPLETE=source k8t > k8t-completion.sh
```

zsh:

```zsh
$ _K8T_COMPLETE=source_zsh k8t > k8t-completion.sh
```

## Concepts

By combining those concepts you can quickly add completely new environments to your deployment pipeline just by
modifying specializing values and sharing the rest.

Check out our examples [here](examples/).

### *Clusters* and *Environments*

k8t comes with a builtin framework for *clusters* and *environments* (e.g. production, staging). This came from the need to be able to deploy
the same application over multiple clusters and in different environments with completely different setups and values.
This idea is helped by the fact that k8t deep-merges values and configs, allowing easy variation through different
stages of your application deployment.

Both *clusters* and *environments* are intentionally working the same way and can be used to add another degree of freedom when
combined. *Environments* however are also available globally, meaning clusters can share environment specific
configuration while specifying differences in those environments.

### Templating

Templating is supported via [Jinja](https://jinja.palletsprojects.com). k8t also comes with some additional
[helper functions](#template-helper-functions) and a [validation function](#validate-templates) with verbose output to
quickly verify the written templates.

#### Template helper functions

* `random_password(N: int)` - generate a random string of length N
* `envvar(key: str, [default])` - get a value from any environment variable with optional default
* `b64encode(value: str)` - encodes a value in base64 (usually required for secrets)
* `b64decode(value: str)` - decodes a value from base64
* `hash(value: str, [method: str])` - hashes a given value (default using `sha256`)
* `get_secret(key: str)` - provides a secret value from a given provider (see [here](#managing-secrets))
* `bool(value: Any)` - casts value to boolean ("true", "on", "yes", "1", 1 are considered as `True`)

## Usage

### Scaffolding

Create a new project folder with a cluster directory and an empty defaults file

```bash
$ k8t new project .
```

Create a new cluster

```bash
$ k8t new cluster MyCluster
```

Create a new environment

```bash
$ k8t new environment staging
```

Generate a new deployment template for cluster MyCluster (for a list of available templates see the `k8t new template --help`)

```bash
$ k8t new template deployment -c MyCluster -e staging
```

### Config management

To ease file access a little bit k8t can open config and value files in your `$EDITOR` or fallback to a sensible
default.

```bash
$ k8t edit values --environment staging
```

```bash
$ k8t edit config --cluster MyCluster
```

### Validate templates

While validation is done before generating, templates can be validated for environment files easily.

```bash
$ k8t validate
```

To validate for clusters/environments the usual options can be used

```bash
$ k8t validate -c MyCluster -e production
```

### Generate manifests

The **--cluster** flag will load variables from a directory. By default the file **default.yaml** in that directory will be
loaded, however an environment can be specified with **--environment**.

```bash
$ k8t gen -c MyCluster -e staging
```

Additionally k8t will attempt to load a file **defaults.yaml** in the root directory. This way a set of default
variables can be specified and selectively overriden via cluster and environment.

Additional values can be given via flag **--value-file** in the form of a file or **--value KEY VALUE**, both can be
supplied multiple times.

Variables will be merged via deep merging. Default merge strategy is left-to-right.

### Overriding templates

Templates can be overriden on a cluster/environment level.

If a file `application.yaml` exists in the root templates folder, simply add a file with the same name to the
cluster/environment template folder.

### Managing secrets

Secrets can be interpolated with the helper function `get_secret`. It requires a key as first argument and providers
are configurable by environment/cluster.

```yaml
foobar: "{{ get_secret('/my-key') }}"
```

#### Providers

##### SSM

Setup secrets on SSM

```yaml
secrets:
  provider: ssm
  region: "eu-central-1"
  prefix: "/foobar"
```

> Keep in mind that SSM parameter names can be formed as a path and  they can only consist of sub-paths divided by slash symbol; each sub-path can be formed as a mix of letters, numbers and the following 3 symbols: `.-_`
>
> Be careful to follow this format when setting up the provider `prefix` and `get_secret(key)`.

##### Random

Random secrets can be generated easily by using the random provider. This provider uses a global dictionary to store
results for the time of the run in python so keys should always produce the same result.

```yaml
secrets:
  provider: random
```

## TODO

* testing needs to be expanded
* the ability to add additional template directories via the CLI
* validation functions for template values (e.g. memory/cpu values)
