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

- [installation](#installation)
- [usage](#usage)
  - [scaffolding](#scaffolding)
  - [validate files](#validate-files)
  - [generate files](#generate-files)
  - [Overriding templates](#overriding-templates)
  - [Managing secrets](#managing-secrets)
    - [SSM](#ssm)
- [TODO](#todo)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## installation

run this

```
$ pip install --user --upgrade k8t
```

**note**: k8t is not Python 2 compatible

## usage

### scaffolding

Create a new project folder with a cluster directory and an empty defaults file

```
$ k8t new project foobar
```

Create a new cluster

```
$ k8t new cluster A
```

Create a new environment

```
$ k8t new environment staging -c A
$ k8t new environment production

```
Generate a new deployment template for cluster A (currently only `deployment` and `service` are supported)

```
$ k8t new template deployment -c A
```

Specify prefixes for secrets

```
$ k8t edit config --cluster A --environment staging
secrets:
  prefix: "staging/application"```
```

Values can be easily added/modified in the same way

```
$ k8t edit values --cluster Ano creds to it anyway or dont know where to get
```

A typical setup should look something like this

```
.deploy/
├── clusters
│   ├── A
│   │   ├── config.yaml
│   │   ├── environments
│   │   │   ├── production
│   │   │   │   ├── config.yaml
│   │   │   │   ├── files
│   │   │   │   ├── templates
│   │   │   │   └── values.yaml
│   │   │   └── staging
│   │   │       ├── config.yaml
│   │   │       ├── files
│   │   │       ├── templates
│   │   │       └── values.yaml
│   │   ├── files
│   │   ├── templates
│   │   └── values.yaml
│   └── local
│       ├── environments
│       ├── files
│       ├── secret.yaml.j2
│       ├── templates
│       │   ├── database.yaml.j2
│       │   └── secret.yaml.j2
│       └── values.yaml
├── config.yaml
├── files
├── templates
│   ├── deployment.yaml.j2
│   └── secret.yaml.j2
└── values.yaml
```

### validate files

While validation is done before generating, templates can be validated for environment files easily.

```
$ k8t validate
```

To validate for clusters/environments the usual options can be used

```
$ k8t validate -c A -e production
```

### generate files

The **--cluster** flag will load variables from a directory. By default the file **default.yaml** in that directory will be
loaded, however an environment can be specified with **--environment**.

```
$ k8t gen -c A -e staging
```

Additionally k8t will attempt to load a file **defaults.yaml** in the root directory. This way a set of default
variables can be specified and selectively overriden via cluster and environment.

Additional values can be given via flag **--value-file** in the form of a file or **--value KEY VALUE**, both can be
supplied multiple times.

Variables will be merged via deep merging. Default merge strategy is left-to-right. For the merge order see the output of

```
$ k8t --help
```

### Overriding templates

Templates can be overriden on a cluster/environment level.

If a file `application.yaml` exists in the root templates folder, simply add a file with the same name to the
cluster/environment template folder.

### Managing secrets

#### SSM

Setup secrets on SSM
```
$ k8t edit config
secrets:
  provider: ssm
  prefix: "foobar"
  ```

## TODO

* testing needs to be expanded
* add more templates for manifest scaffolding
* the ability to add additional template directories via the CLI
* validation functions for template values (e.g. memory/cpu values)
