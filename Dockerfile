ARG BASE_IMAGE
FROM $BASE_IMAGE as ocrd_core_base
ARG FIXUP=echo
MAINTAINER OCR-D
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONIOENCODING utf8
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PIP=pip

ENV MAMBA_EXE=/usr/local/bin/conda
ENV MAMBA_ROOT_PREFIX=/conda
ENV PATH=$MAMBA_ROOT_PREFIX/bin:$PATH
ENV CONDA_EXE=$MAMBA_EXE
ENV CONDA_PREFIX=$MAMBA_ROOT_PREFIX
ENV CONDA_SHLVL='1'

WORKDIR /build-ocrd

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
RUN apt-get update && apt-get -y install \
        ca-certificates \
        gcc \
        make \
        wget \
        time \
        curl \
        sudo \
        git \
    && make get-conda \
    && make deps-conda \
    && python3 -m venv /usr/local \
    && hash -r \
    && make install \
    && eval $FIXUP

WORKDIR /data

CMD ["/conda/bin/ocrd", "--help"]

FROM ocrd_core_base as ocrd_core_test
WORKDIR /build-ocrd
COPY Makefile .
RUN make assets
COPY tests ./tests
COPY .gitmodules .
COPY requirements_test.txt .
RUN pip install -r requirements_test.txt
RUN mkdir /ocrd-data && chmod 777 /ocrd-data

CMD ["yes"]
# CMD ["make", "test", "integration-test"]