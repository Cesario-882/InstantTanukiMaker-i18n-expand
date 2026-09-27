# 狸合器 - 添加了 Linux 兼容

基于 asashari 的 InstantTanukiMaker-en，进一步完善了 i18n 和跨平台兼容性。

> ⚠️ **该仓库已废弃**，关于后续发布请移步
> [Cesario-882/InstantTanukiMaker4Qt](https://github.com/Cesario-882/InstantTanukiMaker4Qt)。
> 本仓库仅作历史存档保留。

## 依赖

- Python 3.10+
- GTK3 运行时（仅限 GNU/Linux）
- 运行依赖见 `requirements.txt`

## 安装

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 运行

```bash
python3 main.py
```

## 打包

`locale` 需外置，不随包分发

## License

本项目采用 GPL 许可，详见 [LICENSE](./LICENSE)。
