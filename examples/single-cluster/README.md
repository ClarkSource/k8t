# Single Cluster

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Creation](#creation)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Creation

Scaffold files

```bash
$ k8t new project single-cluster
$ cd single-cluster
$ k8t new environment staging
$ k8t new environment production
$ k8t new template deployment -n hello-world
$ k8t new template service -n hello-world
$ k8t new template ingress -n hello-world -e production
```

Validate templates

```bash
$ k8t validate
hello-world-deployment.yaml.j2: ✗
- undefined variable: name
- undefined variable: limit_cpu
- undefined variable: replicas
- undefined variable: request_memory
- undefined variable: image_repository
- undefined variable: limit_memory
- undefined variable: ns
- undefined variable: image_tag
- undefined variable: request_cpu
hello-world-service.yaml.j2: ✗
- undefined variable: ns
- undefined variable: traffic_port
- undefined variable: name
```

Modify `values.yaml` and add missing variables

```yaml
ns: default
name: hello-world
replicas: 3
image_repository: hello-world
image_tag: latest

request_memory: 256M
request_cpu: 200m
limit_memory: 256M
limit_cpu: 200m

traffic_port: 3000
```

Verify by running validate command

```bash
$ k8t validate
hello-world-deployment.yaml.j2: ✔
hello-world-service.yaml.j2: ✔
```

Generate templates

```bash
$ k8t gen
---
...
$ k8t gen -e production
---
...
```
