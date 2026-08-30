import json
import os
import locale
import sys

_current = {}
LOCALE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locale")


def get_system_language():
    """获取系统语言，返回语言代码（如 'en', 'zh_CN', 'ja'）"""
    try:
        # 在 Linux 下优先读取环境变量
        lang_env = os.environ.get('LANG', '') or os.environ.get('LC_ALL', '') or os.environ.get('LC_MESSAGES', '')
        if lang_env:
            # 取前两部分，如 'zh_CN.UTF-8' -> 'zh_CN'
            lang_code = lang_env.split('.')[0]
        else:
            # 回退到 locale 模块
            lang_code = locale.getdefaultlocale()[0] or 'en'
    except Exception:
        lang_code = 'en'

    # 如果 lang_code 为空，直接返回 'en'
    if not lang_code:
        return 'en'

    # 处理中文变体：zh_TW, zh_HK -> zh_CN
    if lang_code.startswith('zh_TW') or lang_code.startswith('zh_HK'):
        return 'zh_CN'

    # 只取语言主代码，如 'zh_CN' 不变，'zh' 保持 'zh'（但一般不会有）
    return lang_code


def load_language(lang=None):
    global _current
    if lang is None:
        lang = get_system_language()

    # 尝试加载指定的语言文件
    path = os.path.join(LOCALE_DIR, f"{lang}.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            _current = json.load(f)
    else:
        # 回退到 en
        fallback_path = os.path.join(LOCALE_DIR, "en.json")
        if os.path.exists(fallback_path):
            with open(fallback_path, "r", encoding="utf-8") as f:
                _current = json.load(f)
        else:
            _current = {}


def _(text, **kwargs):
    result = _current.get(text, text)
    if kwargs:
        result = result.format(**kwargs)
    return result


# 启动时自动加载系统语言
load_language()
