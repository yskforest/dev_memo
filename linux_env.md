# Pythonのデフォルトバージョンを変更
```bash
sudo apt install python3.7
vi ~/.bashrc
alias python3='/usr/bin/python3.7'
```

# Virtual Box設定
Virtual BoxにUbuntuをインストール
```bash
sudo apt install gcc make perl
```
デバイス・Guest Additions CDからインストール

# WSL1をVcxSrvでGUI起動

## VcxSrvをインストールして起動
- VcxSrvの起動オプションに下記追加
  - -nowgl
- WSL側の設定、以下コマンド実行
- rvizがXサーバーと正しく通信できるようにする
- GazeboがXサーバーと正しく通信できるようにする
```bash
sudo apt install -y x11-apps
echo 'export DISPLAY=localhost:0.0' >> ~/.bashrc
echo 'export LIBGL_ALWAYS_INDIRECT=""' >> ~/.bashrc
echo 'export GAZEBO_IP=127.0.0.1' >> ~/.bashrc
source ~/.bashrc
```

# WSL2をVcxSrvでGUI起動

## VcxSrvをインストールして起動
- VcxSrvの起動オプションに下記追加
  - -ac -nowgl
```bash
# .bashrc
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0
```

# WSL2でホストPCと通信する
- host PCのIP指定が必要
```bash
roslaunch carla_ros_bridge carla_ros_bridge_with_rviz.launch host:=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
```
- ホストIPは可変なので注意
- またesetの設定でファイヤーウォールをオフを通過するようにする必要がある
- [WSL2/ネットワークがつながらない](https://aquabreath.jp/2020/08/24/wsl2-%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E3%81%8C%E3%81%A4%E3%81%AA%E3%81%8C%E3%82%89%E3%81%AA%E3%81%84/)


## WSL側の設定、以下コマンド実行
- rvizがXサーバーと正しく通信できるようにする
- GazeboがXサーバーと正しく通信できるようにする
```bash
sudo apt install -y x11-apps
echo 'export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0' >> ~/.bashrc
echo 'export LIBGL_ALWAYS_INDIRECT=""' >> ~/.bashrc
echo 'export GAZEBO_IP=127.0.0.1' >> ~/.bashrc
source ~/.bashrc
```

- [WSL2におけるVcXsrvの設定](https://qiita.com/ryoi084/items/0dff11134592d0bb895c)

# WSl2でdocker
- [ついにWSL2+docker+GPUを動かせるようになったらしいので試してみる](https://qiita.com/yamatia/items/a70cbb7d8f5101dc76e9)
- [docker install](https://docs.docker.com/engine/install/ubuntu/)

# wsl2 でapt update
- [WSL2でネットワークのドメインを解決できない場合の対処](https://cartman0.hatenablog.com/entry/2020/07/16/WSL2%E3%81%A7%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E3%81%AE%E3%83%89%E3%83%A1%E3%82%A4%E3%83%B3%E3%82%92%E8%A7%A3%E6%B1%BA%E3%81%A7%E3%81%8D%E3%81%AA%E3%81%84%E5%A0%B4%E5%90%88)
- 上記対応後、再度接続できなくなって再度下記設定して接続できるようになった
  - generateResolvConf = false

# WSL + GPU
- [WindowsにおけるGPUの環境構築](https://zenn.dev/kenn/articles/ac128ed2775370)
- [NVIDIA Docker って今どうなってるの？ (19.11版)](https://qiita.com/ksasaki/items/b20a785e1a0f610efa08)

## 手順
- Windows側でnvidia driverインストール
- Windows 21H2 以降
- wsl2導入
- wsl2でdockerのインストール
- nviida-container-toolkitのインストール
