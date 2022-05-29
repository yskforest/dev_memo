# Nvidia driver install
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update
ubuntu-drivers devices
sudo apt install nvidia-driver-XXX
sudo reboot

nvidia-smi

# docker install
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
docker version
sudo usermod -aG docker $USER

# nvidia container toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# conda package
conda install -c conda-forge opencv
conda install -c open3d-admin open3d
conda install -c evindunn pygame
