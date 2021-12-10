ARG BASE_IMAGE
FROM $BASE_IMAGE
MAINTAINER OCR-D
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONIOENCODING utf8
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

WORKDIR /build-ocrd
COPY ocrd ./ocrd
COPY ocrd_modelfactory ./ocrd_modelfactory/
COPY ocrd_models ./ocrd_models
COPY ocrd_utils ./ocrd_utils
RUN mv ./ocrd_utils/ocrd_logging.conf /etc
COPY ocrd_validators/ ./ocrd_validators
COPY Makefile .
COPY README.md .
COPY LICENSE .
RUN apt-get update && apt-get -y install --no-install-recommends \
    ca-certificates \
    software-properties-common \
    python3-dev \
    python3-pip \
    make \
    wget \
    time \
    curl \
    sudo \
    git \
    && pip3 install --upgrade pip setuptools \
    && make install \
    && rm -rf /build-ocrd

WORKDIR /data

CMD ["/usr/local/bin/ocrd", "--help"]
