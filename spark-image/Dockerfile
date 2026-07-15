FROM apache/spark:3.5.7-java17-python3

USER root

RUN apt update && apt install -y wget && apt install -y build-essential

RUN apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /data && chown -R spark:root /data

RUN mkdir -p /home/spark && chown -R spark:spark /home/spark && chmod 777 /home/spark

RUN mkdir -p /home/spark/.ivy2 && chown -R spark:spark /home/spark/.ivy2

COPY ./install-miniconda.sh /tmp/install-miniconda.sh
RUN chmod +x /tmp/install-miniconda.sh && chown spark:spark /tmp/install-miniconda.sh

COPY ./environment.yml /tmp/environment.yml
RUN chown spark:spark /tmp/environment.yml
USER spark
ENV HOME=/home/spark
RUN bash /tmp/install-miniconda.sh && \
    rm /tmp/install-miniconda.sh && \
    rm /tmp/environment.yml && \
    /home/spark/miniconda3/envs/pyspark_conda_env/bin/pip install --no-cache-dir pytest

ENV PATH="/home/spark/miniconda3/envs/pyspark_conda_env/bin:/opt/spark/bin:/opt/spark/sbin:/home/spark/miniconda3/bin:$PATH"
ENV CONDA_DEFAULT_ENV=pyspark_conda_env