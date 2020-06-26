FROM python:3-alpine

LABEL maintainer="CloudOps <cloudops@clark.de>"

COPY . /app
WORKDIR /app

RUN \
  apk add --no-cache --upgrade git && \
  python3 /app/setup.py install && \
  apk del git && \
  rm -rf /app /var/cache/apk

ENTRYPOINT ["k8t"]
