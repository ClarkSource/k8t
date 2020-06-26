FROM python:3-alpine

LABEL maintainer="CloudOps <cloudops@clark.de>"

COPY . /app
WORKDIR /app

#RUN pip install --user --upgrade /app && rm -rf /app

RUN \
  apk add --no-cache --upgrade git && \
  python3 setup.py install && \
  apk del git && \
  rm -rf /setup /var/cache/apk

ENTRYPOINT ["k8t"]
