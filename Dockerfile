ARG BASE_IMAGE
FROM $BASE_IMAGE
ARG BASE_IMAGE
ARG FIXUP=echo
MAINTAINER OCR-D
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONIOENCODING utf8
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV PIP=pip

WORKDIR /build-ocrd
COPY ocrd ./ocrd
COPY ocrd_modelfactory ./ocrd_modelfactory/
COPY ocrd_models ./ocrd_models
COPY ocrd_utils ./ocrd_utils
RUN mv ./ocrd_utils/ocrd_logging.conf /etc
COPY ocrd_validators/ ./ocrd_validators
COPY ocrd_network/ ./ocrd_network
COPY Makefile .
COPY README.md .
COPY LICENSE .
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
    && make deps-ubuntu \
    && python3 -m venv /usr/local \
    && hash -r \
    && pip install --upgrade pip setuptools \
    && make install \
    && eval $FIXUP \
    && rm -rf /build-ocrd
RUN if echo $BASE_IMAGE | fgrep -q cuda; then \
    pip3 install nvidia-pyindex && \
    pip3 install nvidia-cudnn-cu11==8.6.0.163 && \
    pip3 install nvidia-cublas-cu11 && \
    pip3 install nvidia-cusparse-cu11 && \
    pip3 install nvidia-cusolver-cu11 && \
    pip3 install nvidia-curand-cu11 && \
    pip3 install nvidia-cufft-cu11 && \
    pip3 install nvidia-cuda-runtime-cu11 && \
    pip3 install nvidia-cuda-nvrtc-cu11 && \
    echo /usr/local/lib/python3.8/site-packages/nvidia/cudnn/lib/ >> /etc/ld.so.conf.d/000_cuda.conf && \
    echo /usr/local/lib/python3.8/site-packages/nvidia/cublas/lib/ >> /etc/ld.so.conf.d/000_cuda.conf && \
    echo /usr/local/lib/python3.8/site-packages/nvidia/cusparse/lib/ >> /etc/ld.so.conf.d/000_cuda.conf && \
    echo /usr/local/lib/python3.8/site-packages/nvidia/cusolver/lib/ >> /etc/ld.so.conf.d/000_cuda.conf && \
    echo /usr/local/lib/python3.8/site-packages/nvidia/curand/lib/ >> /etc/ld.so.conf.d/000_cuda.conf && \
    echo /usr/local/lib/python3.8/site-packages/nvidia/cufft/lib/ >> /etc/ld.so.conf.d/000_cuda.conf && \
    echo /usr/local/lib/python3.8/site-packages/nvidia/cuda_runtime/lib/ >> /etc/ld.so.conf.d/000_cuda.conf && \
    echo /usr/local/lib/python3.8/site-packages/nvidia/cuda_nvrtc/lib/ >> /etc/ld.so.conf.d/000_cuda.conf && \
    ldconfig; fi

WORKDIR /data

# remove any entry points from base image
RUN rm -fr /opt/nvidia
ENTRYPOINT []

CMD ["/usr/local/bin/ocrd", "--help"]
