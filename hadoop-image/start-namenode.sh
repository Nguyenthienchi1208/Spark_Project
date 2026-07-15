#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the NameNode data directory based on your hdfs-site.xml.
# The default location is typically within the HADOOP_TMP_DIR.
NAMENODE_DIR="/data/dfs/name/current"

# Check if the NameNode has already been formatted by checking for the 'current' directory.
if [ ! -d "$NAMENODE_DIR" ]; then
  echo "--- First time HDFS format ---"
  # Use -nonInteractive to avoid the confirmation prompt in the script.
  hdfs namenode -format -nonInteractive
  echo "--- HDFS format completed ---"
else
  echo "--- HDFS already formatted ---"
fi

# Start the NameNode service in the foreground.
# This assumes the service startup is part of the base image.
# For example, it might be `hdfs --daemon start namenode` or simply `hdfs namenode`.
# The `exec` command is used to replace the current shell process with the NameNode process,
# which ensures signals are handled correctly.
exec "$HADOOP_HOME/bin/hdfs" namenode