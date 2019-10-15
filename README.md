# k8t

*Pronounced Katie [ˈkeɪti]*

Simple cluster and environment specific aware templating for kubernetes manifests.

## installation

run this

```
$ pip install --user --upgrade .
```

## example

check out https://github.com/ClarkSource/k8s-cd-poc

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
$ k8t new environment staging A
$ k8t new environment production A
```
Setup secrets on SSM

```
$ k8t edit config
secrets:
  provider: ssm
```

Specify prefixes for SSM secrets

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
