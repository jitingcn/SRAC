FROM python:alpine

MAINTAINER jitingcn

RUN echo "http://dl-4.alpinelinux.org/alpine/v3.7/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.7/community" >> /etc/apk/repositories

RUN apk update && \
    apk add --update --no-cache g++ gcc libxslt-dev chromium chromium-chromedriver

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
