FROM python:3-alpine

LABEL maintainer="CloudOps <cloudops@clark.de>"

ARG KUBECTL_VERSION="1.18.0"
ARG KUBEVAL_VERSION="0.15.0"
ARG KUBECTL_SHA="bb16739fcad964c197752200ff89d89aad7b118cb1de5725dc53fe924c40e3f7"
ARG KUBEVAL_SHA="70bff2642a2886c0d9ebea452ffb81f333a956e26bbe0826fd7c6797e343e5aa"

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
