FROM apache/spark:3.5.7-java17-python3

USER root

# 1. Cài đặt các gói hệ thống
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    zip \
    python-is-python3 \
    python3.10-venv \
    && apt-get autoremove -y && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Thiết lập thư mục
RUN mkdir -p /data /home/spark/.ivy2 && \
    chown -R spark:spark /data /home/spark

USER spark
ENV HOME=/home/spark
WORKDIR /home/spark

# 3. Cài đặt Miniconda (Script đã được sửa để dùng /home/spark/miniconda3)
COPY --chown=spark:spark spark-image/install-miniconda.sh /tmp/install-miniconda.sh
RUN bash /tmp/install-miniconda.sh && rm /tmp/install-miniconda.sh

# 4. Tạo môi trường Conda (Dùng đường dẫn tuyệt đối)
COPY --chown=spark:spark spark-image/environment.yml /tmp/environment.yml
RUN /home/spark/miniconda3/bin/conda tos accept \
        --override-channels \
        --channel https://repo.anaconda.com/pkgs/main && \
    /home/spark/miniconda3/bin/conda tos accept \
        --override-channels \
        --channel https://repo.anaconda.com/pkgs/r && \
    /home/spark/miniconda3/bin/conda env create -f /tmp/environment.yml && \
    rm /tmp/environment.yml

# 5. Cấu hình biến môi trường
# Thay 'my_env' bằng đúng tên 'name' trong file environment.yml của bạn
ENV PATH="/home/spark/miniconda3/envs/pyspark_conda_env/bin:/home/spark/miniconda3/bin:$PATH"
ENV PYSPARK_PYTHON="/home/spark/miniconda3/envs/pyspark_conda_env/bin/python"

# 6. Volumes
USER root
VOLUME ["/data", "/home/spark/.ivy2"]
USER spark