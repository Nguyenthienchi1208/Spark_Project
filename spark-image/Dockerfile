FROM apache/spark:3.5.7-java17-python3

# 1. Cài đặt các gói hệ thống cần thiết (Cần quyền root)
USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    zip \
    python-is-python3 \
    python3.10-venv \
    && apt-get autoremove -y && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 2. Thiết lập thư mục và quyền truy cập
RUN mkdir -p /data /home/spark/.ivy2 && \
    chown -R spark:spark /data /home/spark && \
    usermod -d /home/spark spark

# 3. Cài đặt Miniconda (Chạy với user spark)
USER spark
WORKDIR /home/spark
COPY ./install-miniconda.sh /tmp/install-miniconda.sh
RUN bash /tmp/install-miniconda.sh -b -p /home/spark/miniconda3 && \
    rm /tmp/install-miniconda.sh

# 4. Tạo môi trường conda
COPY ./environment.yml /tmp/environment.yml
RUN /home/spark/miniconda3/bin/conda env create -f /tmp/environment.yml && \
    rm /tmp/environment.yml

# 5. Cấu hình biến môi trường cho Spark
# Đảm bảo tên env trong environment.yml là 'my_env'
ENV CONDA_DEFAULT_ENV=my_env
ENV PATH="/home/spark/miniconda3/envs/my_env/bin:$PATH"
ENV PYSPARK_PYTHON="/home/spark/miniconda3/envs/my_env/bin/python"
ENV PYSPARK_DRIVER_PYTHON="/home/spark/miniconda3/envs/my_env/bin/python"

# 6. Thiết lập volumes và user
VOLUME ["/data", "/home/spark/.ivy2"]
USER spark
WORKDIR /home/spark