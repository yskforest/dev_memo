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

## WSl2でdocker
- [ついにWSL2+docker+GPUを動かせるようになったらしいので試してみる](https://qiita.com/yamatia/items/a70cbb7d8f5101dc76e9)
- [docker install](https://docs.docker.com/engine/install/ubuntu/)

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
