FROM python:3-alpine

LABEL maintainer="CloudOps <cloudops@clark.de>"

# Install kubectl
RUN \
  apk add --no-cache openssl curl tar gzip bash ca-certificates && \
  curl -L -o /usr/bin/kubectl https://storage.googleapis.com/kubernetes-release/release/v1.8.0/bin/linux/amd64/kubectl && \
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
