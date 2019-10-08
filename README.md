# kinja

Simple k8s manifest templating with variants.

## installation

run this

```
$ pip install --user --upgrade .
```

## usage

create new folde

This will set up a new project folder with a variants directory and an empty defaults file

```
$ kinja new foobar
```

### generate files

The **--variant** flag will load variables from a directory. By default the file **default.yaml** in that directory will be
loaded, however an environment can be specified with **--environment**.

```
$ kinja gen platform/ --variant cluster1.fragwilhelm.de --environment staging
```

Additionally kinja will attempt to load a file **defaults.yaml** in the root directory. This way a set of default
variables can be specified and selectively overriden via variant and environment.

Additional values can be given via flag **--value-file** in the form of a file or **--value KEY VALUE**, both can be
supplied multiple times.

Variables will be merged via deep merging. Default merge strategy is left-to-right. For the merge order see the output of

```
$ kinja --help
```
