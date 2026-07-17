FROM apache/spark:3.5.7-java17-python3

USER root
RUN apt update && apt install -y wget build-essential && apt-get clean

# 1. Cài đặt Conda
COPY ./install-miniconda.sh /tmp/install-miniconda.sh
RUN bash /tmp/install-miniconda.sh -b -p /opt/miniconda3 && \
    rm /tmp/install-miniconda.sh

# 2. Tạo môi trường và cài conda-pack
COPY ./environment.yml /tmp/environment.yml
RUN /opt/miniconda3/bin/conda env create -f /tmp/environment.yml && \
    /opt/miniconda3/bin/conda install -y -c conda-forge conda-pack && \
    rm /tmp/environment.yml

# 3. Môi trường mặc định cho Driver (spark-client)
ENV PATH="/opt/miniconda3/envs/pyspark_conda_env/bin:$PATH"
ENV PYSPARK_PYTHON="/opt/miniconda3/envs/pyspark_conda_env/bin/python"
ENV PYSPARK_DRIVER_PYTHON="/opt/miniconda3/envs/pyspark_conda_env/bin/python"

# 4. Phân quyền
RUN chown -R spark:spark /opt/miniconda3
USER spark 