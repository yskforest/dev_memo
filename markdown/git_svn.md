# git_svn

## svn to git
```bash
# authors.txt
svn_user1 = Taro Yamada <taro@example.com>
svn_user2 = Hanako Sato <hanako@example.com>

git svn clone https://svn.example.com/svn/project \
  --stdlayout \
  --authors-file=authors.txt \
  --no-metadata \
  project-git

cd project-git
git log --graph --oneline --all

git remote add origin git@gitlab.com:yourname/project-git.git
git push -u origin --all
git push origin --tags
```

## update git
```bash
# svn_update_and_push.sh
#!/bin/bash
cd /path/to/project-git

# SVNの最新を取得
git svn rebase

# GitLabにpush
git push origin --all
git push origin --tags
```

## trunk
```bash
git svn clone https://svn.example.com/svn/project \
  -T trunk \
  --authors-file=authors.txt \
  --no-metadata \
  project-git


```