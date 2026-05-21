# 谷歌验证器

这是一个本地 Python Tk 桌面版 TOTP 验证器，当前界面是极简批量读取模式，适合直接粘贴多行密钥后读取验证码。

## 启动

推荐无终端启动，直接双击：

```text
谷歌验证器.app
```

备用启动方式会打开终端窗口：

```text
启动.command
```

无终端启动器的日志会写入：

```text
data/no_terminal_launcher.log
```

也可以显式使用本目录虚拟环境启动：

```bash
./.venv/bin/python ./main.py
```

说明：启动脚本会自动跳过系统 `python3`，优先使用 `.venv` 或 Homebrew Python 3.11，避免 macOS 自带 Tk 崩溃。

## Windows

Windows 免依赖版本会通过 GitHub Releases 提供，下载 release 里的 `gugeyanzhengqi-windows-amd64.zip`，解压后直接运行 `谷歌验证器.exe` 即可。

## 使用方式

最常用的是直接把多行密钥粘贴进去，每行一个，例如：

```text
QLRCZNFWX3GZRWPY
REITMLTQJPG5DASV
EALSTVUQHHZHZAUO
HMYS7BTKEQLASO2U
```

也支持：

```text
标签,密钥[,digits,period,algorithm]
标签|密钥|digits|period|algorithm
otpauth://totp/Issuer:Account?secret=BASE32&issuer=Issuer
```

说明：当前界面列表默认显示的是密钥本身；`标签` 和 `otpauth` 里的平台/账号信息目前只用于兼容导入格式，不会替换列表里的密钥显示。

默认值：

- `digits=6`
- `period=30`
- `algorithm=SHA1`

## 本地文件

程序会在当前目录生成：

- `secrets.txt`
- `data/python_launcher_path.txt`
- `data/no_terminal_launcher.log`

其中 `secrets.txt` 会保存你当前输入框里的密钥内容，方便下次打开继续使用。

Windows 免依赖版会把 `secrets.txt` 保存到 `谷歌验证器.exe` 所在目录，便于解压后长期保留数据。

注意：当前版本是本地明文保存密钥，仅适合你自己的本机离线使用。请不要把 `secrets.txt`、截图或 release 附件中的个人密钥上传到公开位置。

## 发版检查

本地回归测试：

```bash
python3 -m unittest discover -s tests
python3 -m py_compile main.py
bash -n 启动.command
bash -n 谷歌验证器.app/Contents/MacOS/launch
plutil -lint 谷歌验证器.app/Contents/Info.plist
```

推送 `v*` tag 后，Windows release workflow 会先运行同一组 Python 单元测试，再构建免依赖 zip，并上传：

- `gugeyanzhengqi-windows-amd64.zip`
- `SHA256SUMS.txt`

zip 内包含 `谷歌验证器.exe`、`LICENSE` 和 `README.md`。

## 许可证

本项目使用 MIT License，详见 `LICENSE`。
