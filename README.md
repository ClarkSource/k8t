# kinja

Simple cluster and environment specific aware templating for kubernetes manifests.

## installation

run this

```
$ pip install --user --upgrade .
```

## usage

### scaffolding

Create a new project folder with a cluster directory and an empty defaults file

```
$ kinja new project foobar
```

Create a new cluster

```
$ kinja new cluster A
```

Create a new environment

```
$ kinja new environment staging A
$ kinja new environment production A
```
Setup secrets on SSM

```
$ kinja edit config
secrets:
  provider: ssm
```

Specify prefixes for SSM secrets

```
$ kinja edit config --cluster A --environment staging
secrets:
  prefix: "staging/application"```
```

### validate files

While validation is done before generating, templates can be validated for environment files easily.

```
$ kinja validate
```

To validate for clusters/environments the usual options can be used

```
$ kinja validate -c A -e production
```

### generate files

The **--cluster** flag will load variables from a directory. By default the file **default.yaml** in that directory will be
loaded, however an environment can be specified with **--environment**.

```
$ kinja gen -c A -e staging
```

Additionally kinja will attempt to load a file **defaults.yaml** in the root directory. This way a set of default
variables can be specified and selectively overriden via cluster and environment.

Additional values can be given via flag **--value-file** in the form of a file or **--value KEY VALUE**, both can be
supplied multiple times.

Variables will be merged via deep merging. Default merge strategy is left-to-right. For the merge order see the output of

```
$ kinja --help
```

### Overriding templates

Templates can be overriden on a cluster/environment level.

If a file `application.yaml` exists in the root templates folder, simply add a file with the same name to the
cluster/environment template folder.
