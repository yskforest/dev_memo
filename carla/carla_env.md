# carla env

## Visual Studio 2019でCARLA_0.9.10.1をビルド

### 手順
- コードをクローン
- VS ver ソース修正
  - -G "Visual Studio 15 2017 Win64"　を　-G "Visual Studio 16 2019"　に置換
  - プロジェクト内全置換でOK
- Toolset ソース修正
  - msvc-14.1　を　msvc-14.2 に置換
  - プロジェクト内全置換でOK
- zlibのセットアップ
  - 0.9.10.1のスクリプトは動かないので、[最新のスクリプト](https://github.com/carla-simulator/carla/blob/master/Util/InstallersWin/install_zlib.bat)へ置き換え
- xercescのセットアップ
  - [最新のスクリプト](https://github.com/carla-simulator/carla/blob/master/Util/InstallersWin/install_xercesc.bat)
- boostのセットアップ
  - ↓動くことを確認
  - VS2019ではどうもうまくboostのビルドができなかったので、VS2017でビルドしたものやver0.9.12(VS2019)でビルドしたboostを持ってくる
  - 以下2フォルダをビルド済みのプロジェクトから同フォルダにコピー
    - carla\Build\boost-1.72.0-install
    - carla\Build\boost-1.72.0-source
  - carla/Util/Setup.batのDownload and install Boost(L164)の下記をコメントアウト

```bat
echo %FILE_N% Installing Boost...
call "%INSTALLERS_DIR%install_boost.bat"^
 --build-dir "%INSTALLATION_DIR%"^
 --toolset %TOOLSET%^
 --version %BOOST_VERSION%^
 -j %NUMBER_OF_ASYNC_JOBS%

if %errorlevel% neq 0 goto failed

if not defined install_boost (
    echo %FILE_N% Failed while installing Boost.
    goto failed
)
```

- make PythonAPI
- make launch

### 参考URL
- [Windows で Carla をソースコードからビルドして、インストールする](https://www.kkaneko.jp/tools/win/carla.html)
- [Windows build 0.9.10](https://carla.readthedocs.io/en/0.9.10/build_windows/)
----

# WSL CARLA関連
## ホストPCのCARLAサーバーへアクセス
```bash
# host:= を指定する必要あり
roslaunch carla_autoware_agent carla_autoware_agent.launch town:=Town01 host:=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
```