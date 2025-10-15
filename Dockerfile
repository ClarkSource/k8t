FROM python:3-alpine

LABEL maintainer="Core-Platform <core-platform@clark.io>"

ARG KUBECTL_VERSION="1.32.9"
ARG KUBECTL_SHA="509ae171bac7ad3b98cc49f5594d6bc84900cf6860f155968d1059fde3be5286"

# Download and install tools
RUN apk update && apk upgrade && \
  apk add --no-cache openssl curl tar gzip bash ca-certificates py3-wheel gcc musl-dev

RUN \
  echo -e "${KUBECTL_SHA}  /tmp/kubectl" >> /tmp/CHECKSUMS && \
  curl -L -o /tmp/kubectl "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" && \
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
  pip install /app && \
  which k8t && \
  apk del git gcc musl-dev && \
  rm -rf /app /var/cache/apk

USER 65534

ENTRYPOINT ["k8t"]
