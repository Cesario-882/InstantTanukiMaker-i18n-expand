# 狸合器 - Linux 移植版

基于 asashari 的 InstantTanukiMaker-en，修复了 Linux 下的兼容性问题

## 依赖
- Python 3.10+
- GTK3 运行时（仅限GNU/Linux）

## 安装
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# 注：其运行时会报错，但不要在意那些细节（），GNU/Linux用户请在python3前附加GDK_BACKEND=x11以防止出现奇怪问题
