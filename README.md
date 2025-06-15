# chaos-box

Collection of handy utils written in Python 3

## install

推荐使用 pipx 安装本项目,

```shell
# install from PyPI
pipx install chaos-box --system-site-packages

# install from Test PyPI
pipx install chaos-box \
    --system-site-packages \
    --index-url https://test.pypi.org/simple/ \
    --pip-args "--extra-index-url https://pypi.org/simple/"
```

> 对于 Debian 系统而言, 由于 [`deb-extract`](src/chaos_box/deb_extract.py) 工具用到了 [`python3-debian`](https://salsa.debian.org/python-debian-team/python-debian) 这个 package, 而 `python3-debian` 并没有上传到 PyPI 中, 因此在使用 pipx install 时除了到带上 `--system-site-packages` 选项外, 可能你也需要手动安装下 `python3-debian` package.

```shell
sudo apt install python3-debian
```

> 在本地开发时, 使用 pdm 创建 venv 时也需要添加 `--system-site-packages`, 下面指令中的 `3.11` 是 Python 版本

```shell
# pdm venv backend defaults to virtualenv
pdm venv create -- 3.11 --system-site-packages

# install dependencies and activate venv
pdm install
pdm venv activate
```

## tools

所有命令行工具都可以使用 `-h` 或 `--help` 查看帮助信息, 下面是简要说明,

- deb-extract: 列举当前目录下所有 `.deb` package 并解压到同名目录
- dir-archive: 列举当前目录下所有文件夹, 批量将文件夹创建为同名压缩档, 支持多种压缩档格式
- merge-ip-ranges: 从标准输入或文件中读取 IP addresses 并对其合并与去重
- netstats: 显示各网卡开机以来流量和 packet 计数, 可以使用 regex 过滤网卡名称
- pconv: 将文件中出现的全角标点符号转换为半角标点符号
- rename-with-date: 将目录中特定后缀的文件重命名为 mtime 日期前缀
- rotate-images: 创建 .mp4 或 .gif 格式的可以旋转的头像
- shasum-list: 计算特定目录下所有文件的 hexdigest 并保存到文件中, 支持忽略 .gitignore
- sort-keys: 读取 .json 文件后对 dict 执行 `sort_keys` 后保存
- urlencode: 从标准输入或文件中读取文本并进行 urlencode

## TODO

- [ ] add zstd support on `deb-extract`
