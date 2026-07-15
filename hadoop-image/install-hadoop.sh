#!/bin/bash

FILE_URL=https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
FILE_NAME=hadoop-$HADOOP_VERSION

architecture=$(uname -m)

if [[ "$architecture" == "x86_64" ]]; then
  echo "Architecture: x86_64"
  FILE_URL=https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
  FILE_NAME=hadoop-$HADOOP_VERSION
elif [[ "$architecture" == "aarch64" ]]; then
  echo "Architecture: aarch64"
  FILE_URL=https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION-aarch64.tar.gz
  FILE_NAME=hadoop-$HADOOP_VERSION-aarch64
else
  echo "Architecture: Unknown ($architecture)"
  FILE_URL=https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz
  FILE_NAME=hadoop-$HADOOP_VERSION
fi

echo "FILE_URL: ${FILE_URL}"
echo "FILE_NAME: ${FILE_NAME}"

apt-get update &&
DEBIAN_FRONTEND=noninteractive apt-get install -y wget libzip4 libsnappy1v5 libssl-dev &&
wget $FILE_URL &&
apt-get remove -y wget &&
rm -rf /var/lib/apt/lists/* &&
tar -zxf /$FILE_NAME.tar.gz &&
rm /$FILE_NAME.tar.gz &&
mv hadoop-$HADOOP_VERSION /usr/local/hadoop &&
mkdir -p /usr/local/hadoop/logs