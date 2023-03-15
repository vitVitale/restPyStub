FROM python:3.10.7-slim-bullseye as base
MAINTAINER Vitaly Vasilyuk
USER root

RUN mkdir -m 777 stub

COPY app /stub/app
COPY start.sh /stub/
COPY requirements.txt /stub/

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r /stub/requirements.txt && \
    chmod +x /stub/start.sh

WORKDIR /stub
ENTRYPOINT ["/stub/start.sh"]