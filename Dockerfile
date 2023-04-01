ARG BASE_IMAGE
FROM $BASE_IMAGE
ARG FIXUP=echo
MAINTAINER OCR-D
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONIOENCODING utf8
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PIP=pip3

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
RUN echo 'APT::Install-Recommends "0"; APT::Install-Suggests "0";' >/etc/apt/apt.conf.d/ocr-d.conf
RUN apt-get update && apt-get -y install software-properties-common \
    && apt-get update && apt-get -y install \
        ca-certificates \
        python3-dev \
        python3-pip \
        python3-venv \
        gcc \
        make \
        wget \
        time \
        curl \
        sudo \
        git \
    && make deps-ubuntu \
    && pip3 install --upgrade pip setuptools \
    && hash -r \
    && make install \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && $FIXUP \
    && rm -rf /build-ocrd

WORKDIR /data

CMD ["/usr/local/bin/ocrd", "--help"]
