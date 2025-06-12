# miscbox

Collection of handy utils written in Python 3

## install

推荐使用 pipx 安装本项目,

```shell
# install from PyPI
pipx install miscbox \
    --system-site-packages

# install from Test PyPI
pipx install miscbox \
    --system-site-packages \
    --index-url https://test.pypi.org/simple/ \
    --pip-args "--extra-index-url https://pypi.org/simple/"
```

> 对于 Debian 系统而言, 由于 [`deb-extract`](src/miscbox/deb_extract.py) 工具用到了 [`python3-debian`](https://salsa.debian.org/python-debian-team/python-debian) 这个 package, 而 `python3-debian` 并没有上传到 PyPI 中, 因此在使用 pipx install 时除了到带上 `--system-site-packages` 选项外, 可能你也需要手动安装下 `python3-debian` package.

> 对于本地开发过程中, 使用 pdm 创建 venv 时也需要添加 `--system-site-packages`

```shell
# pdm venv backend defaults to virtualenv
pdm venv create -- 3.11 --system-site-packages

# install dependencies and activate venv
pdm install
pdm venv activate
```

## tools

所有命令行工具都可以使用 `-h` 或 `--help` 查看帮助信息, 下面是简要说明,

- deb-extract: 用于解压 `.deb` package
- dir-archive: 用于批量将当前目录下的所有目录创建为压缩档
- enc-recover: [乱码恢复指北 | Re:Linked](https://blog.outv.im/2019/encoding-guide/)
- merge-ip-ranges: 用于合并与去重 IP addresses, 从标准输入或文件中读取
- mobi-archive: 用于批量将从 vol.moe 下载的 `.mobi` 格式的漫画转换为 `.zip` (即 `.cbz`) 格式, 并不是适用于其它类型的电子书
- net-stats: 显示各网卡开机以来流量
- punc-conv: 将文件中出现的全角标点符号转换为半角标点符号
- rename-with-date: 将目录中特定后缀的文件重命名为带日期前缀 (日期为文件的 mtime)
- rotate-images: 用于创建旋转头像
- shasum-list: 计算特定目录下所有文件的 digest (默认是 sha256sum) 并保存到文件中
- sort-keys: 读取 .json 文件后对 dict 执行 `sort_keys` 后保存
- urlencode: 读取文件或标准输入执行 urlencode

## TODO

- [ ] add zstd support for `deb-extract`
