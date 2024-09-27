ARG BASE_IMAGE
FROM $BASE_IMAGE as ocrd_core_base
ARG FIXUP=echo
MAINTAINER OCR-D
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONIOENCODING utf8
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PIP=pip

WORKDIR /build/core

COPY src ./src
COPY pyproject.toml .
COPY VERSION ./VERSION
COPY requirements.txt ./requirements.txt
RUN mv ./src/ocrd_utils/ocrd_logging.conf /etc
COPY Makefile .
COPY README.md .
COPY LICENSE .
COPY .git ./.git

RUN echo 'APT::Install-Recommends "0"; APT::Install-Suggests "0";' >/etc/apt/apt.conf.d/ocr-d.conf
RUN apt-get update && apt-get -y install software-properties-common \
    && apt-get update && apt-get -y install \
        ca-certificates \
        python3-dev \
        python3-venv \
        gcc \
        make \
        wget \
        time \
        curl \
        sudo \
        git \
    && make deps-ubuntu
RUN python3 -m venv /usr/local \
    && hash -r \
    && make install-dev \
    && eval $FIXUP
# Smoke Test
RUN ocrd --version

WORKDIR /data

CMD ["/usr/local/bin/ocrd", "--help"]

FROM ocrd_core_base as ocrd_core_test
# Optionally skip make assets with this arg
ARG SKIP_ASSETS
WORKDIR /build/core
COPY Makefile .
COPY .gitmodules .
RUN if test -z "$SKIP_ASSETS" || test $SKIP_ASSETS -eq 0 ; then make assets ; fi
COPY tests ./tests
COPY requirements_test.txt .
RUN pip install -r requirements_test.txt
RUN mkdir /ocrd-data && chmod 777 /ocrd-data

CMD ["yes"]
# CMD ["make", "test", "integration-test"]
