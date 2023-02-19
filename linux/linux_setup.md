# ubuntu env


## setup script
```bash
# apt fast
sudo add-apt-repository ppa:apt-fast/stable
sudo apt update
sudo apt -y install apt-fast
# apt,5(default),yes

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

distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

## Pythonのデフォルトバージョンを変更
```bash
sudo apt install python3.7
vi ~/.bashrc
alias python3='/usr/bin/python3.7'
```
