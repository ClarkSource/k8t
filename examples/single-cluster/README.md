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
# Source: hello-world-deployment.yaml.j2
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-world
  namespace: default
  labels:
    app.kubernetes.io/name: hello-world
spec:
  replicas: 3
  revisionHistoryLimit: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: hello-world
  template:
    metadata:
      name: hello-world
      labels:
        app.kubernetes.io/name: hello-world
    spec:
      restartPolicy: Always
      securityContext:
        runAsUser: 1000
      containers:
        - name: hello-world
          image: hello-world:latest
          imagePullPolicy: Always
          resources:
            limits:
              cpu: 200m
              memory: 256M
            requests:
              cpu: 200m
              memory: 256M
---
# Source: hello-world-service.yaml.j2
apiVersion: v1
kind: Service
metadata:
  name: hello-world
  namespace: default
  labels:
    app.kubernetes.io/name: hello-world
spec:
  selector:
    app.kubernetes.io/name: hello-world
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
```
