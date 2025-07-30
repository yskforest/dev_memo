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


##
- [コード品質可視化DockerでSonarQube！WSL2で構築](https://tech.walkit.net/docker-sonarqube)
- https://github.com/dotnet/dotnet-docker
- https://github.com/mono/linux-packaging-msbuild
- https://github.com/SonarSource/sonar-scanner-msbuild
- [Docker イメージから SonarQube をインストールする](https://docs.sonarsource.com/sonarqube/9.9/setup-and-upgrade/install-the-server/#installing-sonarqube-from-the-docker-image)
  - 上記のコマンドで示されているように、 バインド マウントではなくボリュームを使用していることを確認してください 。バインド マウントを使用すると、プラグインが正しく設定されなくなります。
- [](https://community.sonarsource.com/t/environment-variables-documentation-with-missing-placeholders/34848)
  - https://github.com/Daabramov/Sonarqube-for-1c-docker/blob/master/docker-compose.yml
  - 
```bash
SONAR_WEB_JAVAOPTS=-Xmx1G -Xms128m -XX:+HeapDumpOnOutOfMemoryError
SONAR_CE_JAVAOPTS=-Xmx2G -Xms128m -XX:+HeapDumpOnOutOfMemoryError
SONAR_SEARCH_JAVAOPTS=-Xmx2G -Xms2G -XX:MaxDirectMemorySize=1G -XX:+HeapDumpOnOutOfMemoryError
```

##
- powershellでVM作成
- ローカルアカウント作成でインストール
  - [ローカルアカウントで「Windows 11」をセットアップする手段がまた一つふさがれてしまう](https://forest.watch.impress.co.jp/docs/serial/yajiuma/2002453.html)
- 仮想スイッチ有効化
- Windows起動後にデバイスの暗号化オフ
- Windows Update
- シャットダウン
- TPMをオフ
  - エクスポート対応
