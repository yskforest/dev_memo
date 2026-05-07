# 

- [1. Conan](#1-conan)
  - [1.1. Hyper-VからGitLab Package RegistryにUPLOADできない問題](#11-hyper-vからgitlab-package-registryにuploadできない問題)
  - [1.2. Conan導入](#12-conan導入)
  - [1.3. conafile.pyサンプル](#13-conafilepyサンプル)

## 1. Conan
### 1.1. Hyper-VからGitLab Package RegistryにUPLOADできない問題
- Large Send Offload (LSO) の無効化
- Windowsのスタートボタンを 右クリック し、「デバイス マネージャー」 を開きます。
- 「ネットワーク アダプター」 のツリーを展開します。
- 現在通信に使用しているネットワークアダプタ（例: Microsoft Hyper-V Network Adapter など）を右クリックし、「プロパティ」 を開きます。
- 「詳細設定」 タブを開きます。
- プロパティのリストから以下の項目を探し、値を 「無効 (Disabled)」 に変更します。
- Large Send Offload Version 2 (IPv4) （日本語名: Large Send Offload V2 (IPv4) または 一括送信オフロード V2 など）

### 1.2. Conan導入
```bash
# デフォルトの公開レジストリ（conancenter）を削除する
conan remote remove conancenter
# 初期化
conan profile detect

conan remote add gitlab http://XXX:8929/api/v4/projects/{ID}/packages/conan
conan remote login gitlab {USER} -p {TOKEN}

# ビルド済みバイナリをパッケージ化（Releaseビルドの例）
conan export-pkg . -s build_type=Release --version "latest+build01"

# パッケージ名/バージョン を指定してアップロード
conan upload "mycommonlib/latest" -r gitlab -c

# DL側
conan list "mycommonlib/latest:*" -r gitlab
# conan install . -s build_type=Release -s compiler.version=191 -s compiler.cppstd=14
conan install --requires="mycommonlib/latest" --deployer=deploy.py -s build_type=Release -s compiler.version=191 -s compiler.cppstd=14 --update
```

### 1.3. conafile.pyサンプル
```python
from conan import ConanFile
from conan.tools.scm import Git
from conan.tools.files import copy
import os

class MyCommonLibConan(ConanFile):
    name = "mycommonlib"
    # version = "1.0.0"
    
    # どの環境用のバイナリかを識別するための設定
    settings = "os", "compiler", "build_type", "arch"

    def export(self):
        # レシピがエクスポートされるタイミングでGitの情報を取得
        git = Git(self, self.recipe_folder)
        # リモートURLと現在のコミットハッシュを conandata.yml に自動保存する
        git.coordinates_to_conandata()

    def package(self):
        # 現在のフォルダ(source_folder)から、パッケージ化フォルダへファイルをコピー
        copy(self, "*.h", src=os.path.join(self.source_folder, "include"), dst=os.path.join(self.package_folder, "include"), keep_path=False)
        copy(self, "*.lib", src=os.path.join(self.source_folder, "lib"), dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        # このパッケージを利用する側にリンクさせる .lib の名前 (拡張子なし)
        self.cpp_info.libs = ["MyCommonLib"]
```
