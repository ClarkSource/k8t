# Single Cluster

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Creation](#creation)
  - [Secrets](#secrets)
  - [Production](#production)
    - [Secrets](#secrets-1)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Creation

Scaffold files

```bash
$ k8t new project single-cluster
$ cd single-cluster
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
...
```

### Secrets

We would like to add a password as an environment variable to the pods. For now we'll add the secret resource and specify a key

```bash
k8t new template secret -n hello-world
```

edit templates/hello-world-secret.yaml.j2 to look like this:

```yaml
apiVersion: v1
kind: Secret
metadata:
  namespace: "{{ ns }}"
  name: "{{ name }}"
  labels:
    app.kubernetes.io/name: "{{ name }}"
type: Opaque
data:
  PASSWORD: "{{ get_secret('/application') | b64encode }}"
```

running validation will now show an error

```bash
$ k8t validate
hello-world-deployment.yaml.j2: ✔
hello-world-secret.yaml.j2: ✗
- No secrets provider configured
hello-world-service.yaml.j2: ✔
```

to fix this we edit `config.yaml`. For the purpose of this example we use the random provider. This will always return
the same password for the same key.

```yaml
secrets:
  provider: random
```

### Production

We want our production environment to be created with an ingress resource

```bash
$ k8t new environment production
$ k8t new template ingress -n hello-world -e production
```

Now validate

```bash
k8t validate
hello-world-deployment.yaml.j2: ✔
hello-world-ingress.yaml.j2: ✗
- undefined variable: domain
hello-world-service.yaml.j2: ✔
```

We need to set the external domain and also want our resources to be created in a separate namespace.

Edit the environment value file `environments/production/values.yaml`

```yaml
domain: foobar.example.org
ns: production
```

Validation will now work for the environment and we can generate our resources

```bash
$ k8t gen -e production
...
```

#### Secrets

In a real world example you would likely want to pull secrets from an external source. We can now configure ssm as our
secret provider in `environments/production/config.yaml`

```yaml
secrets:
  provider: ssm
  prefix: '/production'
```

This will now attempt to request a secret value from AWS SSM with the key `/production/application` when generating
templates for production.
