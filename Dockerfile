FROM ubuntu:16.04
MAINTAINER OCR-D
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONIOENCODING utf8
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

WORKDIR /build-ocrd
COPY Makefile .
RUN apt-get update && \
    apt-get -y install --no-install-recommends \
    ca-certificates \
    make \
    git \
    libglib2.0.0 \
    libsm6 \
    libxrender1 \
    libxext6
RUN make deps-ubuntu
RUN pip3 install --upgrade pip
COPY ocrd ./ocrd
COPY setup.py .
COPY requirements.txt .
COPY README.rst .
COPY LICENSE .
RUN make deps-pip install

ENTRYPOINT ["/usr/local/bin/ocrd"]
