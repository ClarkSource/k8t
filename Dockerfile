FROM python:3-alpine

LABEL maintainer="CloudOps <cloudops@clark.de>"

ARG KUBECTL_VERSION="1.20.5"
ARG KUBEVAL_VERSION="0.16.1"
ARG KUBECTL_SHA="7f9dbb80190945a5077dc5f4230202c22f68f9bd7f20c213c3cf5a74abf55e56"
ARG KUBEVAL_SHA="2d6f9bda1423b93787fa05d9e8dfce2fc1190fefbcd9d0936b9635f3f78ba790"

# Download and install tools
RUN apk update && apk upgrade && \
    apk add --no-cache openssl curl tar gzip bash ca-certificates py3-wheel

RUN \
  echo -e "${KUBECTL_SHA}  /tmp/kubectl\n${KUBEVAL_SHA}  /tmp/kubeval.tar.gz" >> /tmp/CHECKSUMS && \
  curl -L -o /tmp/kubectl "https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
  curl -L -o /tmp/kubeval.tar.gz "https://github.com/instrumenta/kubeval/releases/download/v${KUBEVAL_VERSION}/kubeval-linux-amd64.tar.gz" && \
  sha256sum /tmp/kub* && \
  sha256sum -c /tmp/CHECKSUMS && \
  # install kubectl
  mv /tmp/kubectl /usr/bin/kubectl && \
  chmod +x /usr/bin/kubectl && \
  # install kubeval
  mkdir /opt/kubeval && \
  tar -xzf /tmp/kubeval.tar.gz -C /opt/kubeval && \
  ln -s /opt/kubeval/kubeval /usr/bin/kubeval && \
  pip install --upgrade awscli

# Install app
COPY . /app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN \
  apk add --no-cache --upgrade git && \
  which pip && \
  which python && \
  pip install --use-feature=in-tree-build /app && \
  which k8t && \
  apk del git && \
  rm -rf /app /var/cache/apk

USER 65534

ENTRYPOINT ["k8t"]
