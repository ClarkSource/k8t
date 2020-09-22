FROM python:3-alpine

LABEL maintainer="CloudOps <cloudops@clark.de>"

ARG KUBECTL_VERSION="1.18.0"

# Install kubectl & aws-cli
RUN \
  apk add --no-cache openssl curl tar gzip bash ca-certificates aws-cli && \
  curl -L -o /usr/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl && \
  chmod +x /usr/bin/kubectl && \
  kubectl version --client

# Install app
COPY . /app
WORKDIR /app

RUN \
  apk add --no-cache --upgrade git && \
  python3 /app/setup.py install && \
  apk del git && \
  rm -rf /app /var/cache/apk

ENTRYPOINT ["k8t"]
