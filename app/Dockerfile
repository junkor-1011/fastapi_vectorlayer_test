ARG BASE_IMAGE=ubuntu:latest
FROM $BASE_IMAGE

# system update & package install
RUN apt-get -y update && \
    apt-get install -y --no-install-recommends \
    # build-essential \
    unzip bzip2 \
    openssl libssl-dev \
    curl wget \
    ca-certificates \
    locales \
    sudo \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add Tini
ENV TINI_VERSION v0.19.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# 一般ユーザーアカウントを追加
ARG USER_NAME=app
ARG USER_UID=1000
ARG PASSWD=password

RUN useradd -m -s /bin/bash -u $USER_UID $USER_NAME && \
    gpasswd -a $USER_NAME sudo && \
    echo "${USER_NAME}:${PASSWD}" | chpasswd && \
    echo "${USER_NAME} ALL=(ALL) ALL" >> /etc/sudoers

# FastAPIのソースコードなどをコンテナ内へCOPY
COPY ./app /app/app

# conda用準備
ENV CONDA_DIR=/opt/conda \
    CONDA_TMP_DIR=/tmp/conda \
    HOME=/home/$USER_NAME \
    SHELL=/bin/bash
RUN mkdir -p $CONDA_DIR && \
    mkdir -p $CONDA_TMP_DIR && \
    chown $USER_NAME:$USER_UID $CONDA_DIR && \
    chown $USER_NAME:$USER_UID $CONDA_TMP_DIR
# yamlファイルの取り込み
ARG CONDA_YAML="./conda_packages.yml"
COPY $CONDA_YAML /tmp/conda_packages.yml
RUN chown -R ${USER_NAME}:${USER_NAME} /app


USER $USER_NAME

# miniconda
ARG MINICONDA_VERSION=py37_4.8.3-Linux-x86_64
ARG MINICONDA_MD5=751786b92c00b1aeae3f017b781018df
ENV PATH=${CONDA_DIR}/bin:$PATH

RUN cd /tmp && \
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-${MINICONDA_VERSION}.sh && \
    echo "${MINICONDA_MD5} *Miniconda3-${MINICONDA_VERSION}.sh" | md5sum -c - && \
    /bin/bash Miniconda3-${MINICONDA_VERSION}.sh -f -b -p $CONDA_TMP_DIR && \
    rm Miniconda3-${MINICONDA_VERSION}.sh && \
    $CONDA_TMP_DIR/bin/conda update -n base -c defaults conda --yes && \
    $CONDA_TMP_DIR/bin/conda env create -f /tmp/conda_packages.yml -p $CONDA_DIR && \
    rm -rf $HOME/.cache/* && \
    rm -rf $CONDA_TMP_DIR/*

WORKDIR /app

# ***
# ENV PATH $PATH:/home/${USER_NAME}/.local/bin

# Configration
EXPOSE 8000

# Execute
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--proxy-headers", "--forwarded-allow-ips", "*"]
