#!/bin/bash

mkdir -p ~/miniconda3

architecture=$(uname -m)

if [[ "$architecture" == "x86_64" ]]; then
  echo "Architecture: x86_64"
  wget https://repo.anaconda.com/miniconda/Miniconda3-py313_25.7.0-2-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
elif [[ "$architecture" == "aarch64" ]]; then
  echo "Architecture: aarch64"
  wget https://repo.anaconda.com/miniconda/Miniconda3-py313_25.7.0-2-Linux-aarch64.sh -O ~/miniconda3/miniconda.sh
else
  echo "Architecture: Unknown ($architecture)"
  wget https://repo.anaconda.com/miniconda/Miniconda3-py313_25.7.0-2-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
fi

bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3 &&
rm ~/miniconda3/miniconda.sh &&
export PATH="/home/spark/miniconda3/bin:$PATH" &&
conda init --all &&
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main &&
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r &&
conda env create -y -f /tmp/environment.yml