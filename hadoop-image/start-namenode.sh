#!/bin/bash

set -e

NAMENODE_DIR="/data/dfs/name/current"

# Format HDFS lần đầu
if [ ! -d "$NAMENODE_DIR" ]; then
    echo "=== First time HDFS format ==="
    hdfs namenode -format -nonInteractive
    echo "=== HDFS format completed ==="
else
    echo "=== HDFS already formatted ==="
fi

echo "=== Starting NameNode ==="

# Chạy NameNode ở background
"$HADOOP_HOME/bin/hdfs" namenode &
NN_PID=$!

echo "=== Waiting for HDFS to become available ==="

# Chờ HDFS sẵn sàng
until hdfs dfs -ls / >/dev/null 2>&1; do
    sleep 2
done

echo "=== Initializing HDFS directories ==="

# Tạo các thư mục cần thiết
hdfs dfs -mkdir -p /user
hdfs dfs -mkdir -p /user/spark
hdfs dfs -chown spark:supergroup /user/spark

hdfs dfs -mkdir -p /tmp
hdfs dfs -chmod 1777 /tmp

hdfs dfs -mkdir -p /spark-events
hdfs dfs -chmod 777 /spark-events

echo "=== HDFS initialization completed ==="

# Giữ container chạy
wait $NN_PID