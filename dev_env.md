# Visual StudioでC++ OpenCV

### OpenCVの入手
- Releasesのバイナリを入手
- [OpenCV](https://opencv.org/releases/)
- c/opencv を推奨
### パスを通す
- 環境変数→pathに追加
- C:\opencv\build\x64\vc15\bin

### プロジェクト設定
- [VisualStudio2019 + OpenCV 導入](https://qiita.com/koteko/items/60936f34f21d7decf0b5)
- [OpenCV 4.5.3をVisual Studio 2019から使用](https://qiita.com/h-adachi/items/aad3401b8900438b2acd)
- [環境変数の設定なしで簡単にOpenCVの開発環境を整える話。](https://veresk.hatenablog.com/entry/2020/03/02/183000#%E3%83%A9%E3%82%A4%E3%83%96%E3%83%A9%E3%83%AA%E3%83%87%E3%82%A3%E3%83%AC%E3%82%AF%E3%83%88%E3%83%AA%E3%81%AE%E6%8C%87%E5%AE%9A%E3%82%92%E3%81%97%E3%82%88%E3%81%86)

# Visual StudioでC++ OpenGL GLFW
NuGetでインストール可能なのでそちらが楽

GLFWの入手
- [GLFW DL](https://www.glfw.org/download.html)

プロジェクト設定
-  [GLFWでOpenGLを始めるには in 2019 on Windows](https://qiita.com/kcha4tsubuyaki/items/7d6388129714ca6c48ea)

参考 
- [OpenGLでカメラ画像を表示](https://13mzawa2.hateblo.jp/entry/2016/08/04/210552)

# Visual Studio 2019でWindows8.1 SDKを使う
CARLAのビルドに必要

- [Visual Studio 2019で Windows SDK 8.1 を利用する方法](https://kagasu.hatenablog.com/entry/2019/05/08/223709)
- [Windows SDK and emulator archive](https://developer.microsoft.com/en-us/windows/downloads/sdk-archive/)
- [Windows 8.1 SDK](https://go.microsoft.com/fwlink/p/?LinkId=323507)

# linux SUMO install
[add-apt-repositoryを使わないでPPAを追加する](https://www.usagi1975.com/2019152355/)
[SUMOの公開鍵を取得](https://launchpad.net/~sumo/+archive/ubuntu/stable)

```bash
# sudo add-apt-repository ppa:sumo/stable に相当
apt-key adv --keyserver keyserver.ubuntu.com --recv 0x4B339D18DD12CA62CA0E400F87637B2A34012D7A
sudo apt-get update

# ppa:sumo/stable Ubuntu18.04
deb https://ppa.launchpadcontent.net/sumo/stable/ubuntu bionic main 
deb-src https://ppa.launchpadcontent.net/sumo/stable/ubuntu bionic main 


echo 'deb https://ppa.launchpadcontent.net/sumo/stable/ubuntu bionic main' \
         | sudo tee /etc/apt/sources.list.d/sumo_stable_ubuntu_bionic_main.list
```