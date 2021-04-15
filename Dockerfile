FROM python:3-alpine

LABEL maintainer="CloudOps <cloudops@clark.de>"

ARG KUBECTL_VERSION="1.20.5"
ARG KUBEVAL_VERSION="v0.16.1"
ARG KUBECTL_SHA="7f9dbb80190945a5077dc5f4230202c22f68f9bd7f20c213c3cf5a74abf55e56"
ARG KUBEVAL_SHA="2d6f9bda1423b93787fa05d9e8dfce2fc1190fefbcd9d0936b9635f3f78ba790"

# Install aws-cli & dependencies
RUN apk add --no-cache openssl curl tar gzip bash ca-certificates aws-cli

# Download and install tools
RUN \
  echo -e "${KUBECTL_SHA}  /tmp/kubectl\n${KUBEVAL_SHA}  /tmp/kubeval.tar.gz" >> /tmp/CHECKSUMS && \
  curl -L -o /tmp/kubectl "https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
  curl -L -o /tmp/kubeval.tar.gz "https://github.com/instrumenta/kubeval/releases/download/${KUBEVAL_VERSION}/kubeval-linux-amd64.tar.gz" && \
  sha256sum /tmp/kub* && \
  sha256sum -c /tmp/CHECKSUMS && \
  # install kubectl
  mv /tmp/kubectl /usr/bin/kubectl && \
  chmod +x /usr/bin/kubectl && \
  # install kubeval
  mkdir /opt/kubeval && \
  tar -xzf /tmp/kubeval.tar.gz -C /opt/kubeval && \
  ln -s /opt/kubeval/kubeval /usr/bin/kubeval

# Install app
COPY . /app
WORKDIR /app

RUN \
  apk add --no-cache --upgrade git && \
  python3 /app/setup.py install && \
  apk del git && \
  rm -rf /app /var/cache/apk

ENTRYPOINT ["k8t"]
