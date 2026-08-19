# InstantTanukiMaker i18n Expand

基于 [arashari/InstantTanukiMaker](https://github.com/arashari/InstantTanukiMaker) 的跨平台移植 + 中文语言扩展版本。（但是情况不太乐观）

## ✅ 当前状态

- ✅ 曾在 Ubuntu 26.04 LTS(Kubuntu) 下通过原型测试（不全面）
- ✅ 中文界面支持 (`zh.json`)
- ✅ 素材中文文件夹名自动映射（除界面背景之外）
- ⚠️ 极其不稳定，wxPython简直和GTK八字不合
- ⚠️ 等待社区接手维护

## 🚀 快速开始

```bash
# 克隆仓库
git clone https://github.com/Cesarion882/InstantTanukiMaker-i18n-expand
cd InstantTanukiMaker-i18n-expand

# 安装依赖（Ubuntu/Debian）
sudo apt install python3-wxgtk4.0 python3-numpy python3-opencv python3-pil python3-natsort

# 运行，使用X11后端的原因是在GTK Wayland下目前仍有问题
GDK_BACKEND=x11 GDK_GL=disable python3 main.py
