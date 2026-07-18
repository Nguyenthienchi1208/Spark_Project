#!/bin/bash
set -e

# Sử dụng đường dẫn tuyệt đối, KHÔNG dùng ~
INSTALL_DIR="/home/spark/miniconda3"
mkdir -p "$INSTALL_DIR"

architecture=$(uname -m)
CONDA_SH="/home/spark/miniconda3/miniconda.sh"

if [[ "$architecture" == "x86_64" ]]; then
  echo "Architecture: x86_64"
  wget https://repo.anaconda.com/miniconda/Miniconda3-py313_25.7.0-2-Linux-x86_64.sh -O "$CONDA_SH"
elif [[ "$architecture" == "aarch64" ]]; then
  echo "Architecture: aarch64"
  wget https://repo.anaconda.com/miniconda/Miniconda3-py313_25.7.0-2-Linux-aarch64.sh -O "$CONDA_SH"
else
  echo "Architecture: Unknown ($architecture)"
  wget https://repo.anaconda.com/miniconda/Miniconda3-py313_25.7.0-2-Linux-x86_64.sh -O "$CONDA_SH"
fi

# Cài đặt Miniconda
bash "$CONDA_SH" -b -u -p "$INSTALL_DIR"
rm "$CONDA_SH"