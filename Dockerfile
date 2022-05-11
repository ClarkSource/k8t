FROM python:3-alpine

LABEL maintainer="CloudOps <cloudops@clark.de>"

ARG KUBECTL_VERSION="1.22.6"
ARG KUBECTL_SHA="1ab07643807a45e2917072f7ba5f11140b40f19675981b199b810552d6af5c53"

# Download and install tools
RUN apk update && apk upgrade && \
  apk add --no-cache openssl curl tar gzip bash ca-certificates py3-wheel gcc musl-dev

RUN \
  echo -e "${KUBECTL_SHA}  /tmp/kubectl" >> /tmp/CHECKSUMS && \
  curl -L -o /tmp/kubectl "https://storage.googleapis.com/kubernetes-release/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
  sha256sum /tmp/kub* && \
  sha256sum -c /tmp/CHECKSUMS && \
  # install kubectl
  mv /tmp/kubectl /usr/bin/kubectl && \
  chmod +x /usr/bin/kubectl && \
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
  apk del git gcc musl-dev && \
  rm -rf /app /var/cache/apk

USER 65534

ENTRYPOINT ["k8t"]
