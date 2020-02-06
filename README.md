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

k8t comes with a builtin framework for *clusters* and *environments* (e.g. production, staging). This came from the need to be able to deploy
the same application over multiple clusters and in different environments with completely different setups and values.
This idea is helped by the fact that k8t deep-merges values and configs, allowing easy variation through different
stages of your application deployment.

Combining these features with the power of jinja you can quickly add completely new environments to your deployment
pipeline just by modifying specializing values and sharing the rest.

Check out the examples [here](examples/).

## Usage

### Scaffolding

Create a new project folder with a cluster directory and an empty defaults file

```bash
$ k8t new project .
```

Create a new cluster

```bash
$ k8t new cluster A
```

Create a new environment

```bash
$ k8t new environment staging
```

Generate a new deployment template for cluster A (for a list of available templates see the `k8t new template --help`)

```bash
$ k8t new template deployment -c A
```

### Config management

To ease file access a little bit k8t can open config and value files in your `$EDITOR` with a fallback to `vim`

```bash
$ k8t edit values --environment staging
```

```bash
$ k8t edit config --cluster A
```

### Validate templates

While validation is done before generating, templates can be validated for environment files easily.

```bash
$ k8t validate
```

To validate for clusters/environments the usual options can be used

```bash
$ k8t validate -c A -e production
```

### Generate manifests

The **--cluster** flag will load variables from a directory. By default the file **default.yaml** in that directory will be
loaded, however an environment can be specified with **--environment**.

```bash
$ k8t gen -c A -e staging
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
foobar: "{{ get_secret('/my-key/') }}"
```

#### Providers

##### SSM

Setup secrets on SSM

```yaml
secrets:
  provider: ssm
  prefix: "/foobar"
```

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
