# chaos-box

Collection of handy utils written in Python 3

## install

推荐使用 pipx 安装本项目,

```shell
# install from PyPI
pipx install chaos-box

# install from Test PyPI
pipx install chaos-box \
    --index-url https://test.pypi.org/simple/ \
    --pip-args "--extra-index-url https://pypi.org/simple/"
```

## tools

所有命令行工具都可以使用 `-h` 或 `--help` 查看帮助信息, 下面是简要说明,

- archive-dirs: 列举当前目录下所有文件夹, 批量将文件夹创建为同名压缩档, 支持多种压缩档格式
- archive-mobi: 一个将 vol.moe 下载的 mobi 漫画文件转换为多种压缩档格式的小工具, 很久没用了, 可能缺乏维护
- deb-extract: 列举当前目录下所有 `.deb` package 并解压到同名目录
- merge-ip-ranges: 从标准输入或文件中读取 IP addresses 并对其合并与去重
- netstats: 显示各网卡开机以来流量和 packet 计数, 可以使用 regex 过滤网卡名称
- pconv: 将文件中出现的全角标点符号转换为半角标点符号
- qbt-dump: 导出 .torrent 和 qBittorrent .fastresume 文件内容
- qbt-migrate: 迁移 qBittorrent BT_backup 目录中的 save_path 和 qBt-category
- qrcode-merge: 将 qrcode-split 拆分后的文件合并为原文件
- qrcode-split: 将任意 text 或 binary 文件拆分成一系列 QR code 文件
- rename-with-date: 将目录中特定后缀的文件重命名为 mtime 日期前缀
- rotate-images: 创建 .mp4 或 .gif 格式的可以旋转的头像
- shasum-list: 计算特定目录下所有文件的 hexdigest 并保存到文件中, 支持忽略 .gitignore
- sort-keys: 读取 .json 文件后对 dict 执行 `sort_keys` 后保存
- urlencode: 从标准输入或文件中读取文本并进行 urlencode

## TODO

- [ ] add zstd support on `deb-extract`
