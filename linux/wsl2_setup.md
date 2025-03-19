# wsl2_setup

## wsl2有効化
```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

## WSL2をVcxSrvでGUI起動
### WSL側の設定、以下コマンド実行
- rvizがXサーバーと正しく通信できるようにする
- GazeboがXサーバーと正しく通信できるようにする
```bash
sudo apt install -y x11-apps
echo 'export HOSTIP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')' >> ~/.bashrc
echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0' >> ~/.bashrc
echo 'export LIBGL_ALWAYS_INDIRECT=""' >> ~/.bashrc
echo 'export GAZEBO_IP=127.0.0.1' >> ~/.bashrc
source ~/.bashrc
export HOSTIP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export DISPLAY=${HOSTIP}:0
export LIBGL_ALWAYS_INDIRECT=""
export GAZEBO_IP=127.0.0.1
```



### VcxSrvをインストールして起動
- VcxSrvの起動オプションに下記追加
  - -ac -nowgl
- [WSL2におけるVcXsrvの設定](https://qiita.com/ryoi084/items/0dff11134592d0bb895c)

### WSL2でホストPCと通信する
- host PCのIP指定が必要
```bash
roslaunch carla_ros_bridge carla_ros_bridge_with_rviz.launch host:=$HOSTIP
```
- ホストIPは可変なので注意
- ファイヤーウォールがesetの場合設定でファイヤーウォールをオフを通過するようにする必要がある
- [WSL2/ネットワークがつながらない](https://aquabreath.jp/2020/08/24/wsl2-%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E3%81%8C%E3%81%A4%E3%81%AA%E3%81%8C%E3%82%89%E3%81%AA%E3%81%84/)

## docker install
- [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
```bash
# Uninstall old versions
sudo apt-fast update
sudo apt-fast install ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-fast update
sudo apt-fast install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# addional
sudo usermod -aG docker ${USER}
```

## nvidia-docker2
- [Installation Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
      && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
      && curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
            sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
            sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-fast update
sudo apt-fast install -y nvidia-docker2
```

## wsl2 docker
- [Windows 10 + WSL 2 でDocker環境を構築する（Docker Desktop有料化対策）](https://blog.ecbeing.tech/entry/2021/09/07/150000)
```bash
sudo service docker start
sudo service docker status
# 起動しない場合
sudo update-alternatives --config iptables
# 1を選択してEnter
sudo service docker start
```

```json:/etc/docker/daemon.json
{
  "hosts": [
    "unix:///var/run/docker.sock",
    "tcp://127.0.0.1:2375"
  ]
}
```

## wsl2 でapt update
- [WSL2でネットワークのドメインを解決できない場合の対処](https://cartman0.hatenablog.com/entry/2020/07/16/WSL2%E3%81%A7%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E3%81%AE%E3%83%89%E3%83%A1%E3%82%A4%E3%83%B3%E3%82%92%E8%A7%A3%E6%B1%BA%E3%81%A7%E3%81%8D%E3%81%AA%E3%81%84%E5%A0%B4%E5%90%88)
- 上記対応後、再度接続できなくなって再度下記設定して接続できるようになった
  - generateResolvConf = false

## WSL + GPU
- [WindowsにおけるGPUの環境構築](https://zenn.dev/kenn/articles/ac128ed2775370)
- [NVIDIA Docker って今どうなってるの？ (19.11版)](https://qiita.com/ksasaki/items/b20a785e1a0f610efa08)

### 手順
- Windows側でnvidia driverインストール
- Windows 21H2 以降
- wsl2導入
- wsl2でdockerのインストール
- nviida-container-toolkitのインストール

## docker build時にaptがしくる
ホスト側のネットワークを使う
ホスト側のネットワークを使って問題ない場合は、ホスト側のネットワークを使ってビルドすればよい
「docker image build」には「--network」オプションはあるので。こんな感じで。
```sh
docker image build --network host -t kazuhira/apache2:latest .
```

## 
```bash
sudo usermod -aG docker $USER
getent group docker
```