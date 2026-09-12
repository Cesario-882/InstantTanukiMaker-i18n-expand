import json
import os
import locale
from typing import Optional, Dict

# 全局变量
_current: Dict[str, str] = {}
_current_lang: str = "en"
LOCALE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locale")

# 确保 locale 目录存在
os.makedirs(LOCALE_DIR, exist_ok=True)


def get_system_language() -> str:
    """获取系统语言，返回语言代码（如 'en', 'zh_CN', 'ja'）"""
    try:
        # 在 Linux 下优先读取环境变量
        lang_env = os.environ.get('LANG', '') or os.environ.get('LC_ALL', '') or os.environ.get('LC_MESSAGES', '')
        if lang_env:
            lang_code = lang_env.split('.')[0]
        else:
            lang_code = locale.getdefaultlocale()[0] or 'en'
    except Exception:
        lang_code = 'en'

    if not lang_code:
        return 'en'

    # 处理中文变体：zh_TW, zh_HK, zh -> zh_CN
    if lang_code.startswith('zh'):
        return 'zh_CN'

    # 处理日语 - 返回 ja，但实际加载空字典
    if lang_code.startswith('ja'):
        return 'ja'

    return 'en'


def load_language(lang: Optional[str] = None) -> bool:
    """
    加载指定语言的 JSON 文件
    如果找不到指定语言，回退到英语
    日语返回空字典（显示原始键名）
    返回是否成功加载
    """
    global _current, _current_lang

    if lang is None:
        lang = get_system_language()

    _current_lang = lang

    # 日语：使用空字典，显示原始键名
    if lang == 'ja':
        _current = {}
        return True

    # 尝试加载指定的语言文件
    path = os.path.join(LOCALE_DIR, f"{lang}.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                _current = json.load(f)
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load locale {lang}: {e}")

    # 回退到 en
    fallback_path = os.path.join(LOCALE_DIR, "en.json")
    if os.path.exists(fallback_path):
        try:
            with open(fallback_path, "r", encoding="utf-8") as f:
                _current = json.load(f)
            _current_lang = "en"
            return True
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load fallback locale: {e}")

    _current = {}
    _current_lang = "en"
    return False


def _(text: str, **kwargs) -> str:
    """
    翻译文本
    用法: _("Hello") 或 _("Hello {name}", name="World")
    如果找不到翻译，返回原文本
    """
    result = _current.get(text, text)
    if kwargs:
        try:
            result = result.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return result


def get_current_language() -> str:
    """获取当前使用的语言代码"""
    return _current_lang


def get_all_keys() -> list:
    """获取所有翻译键"""
    return list(_current.keys())


def reload_language() -> bool:
    """重新加载当前语言"""
    return load_language(_current_lang)


def has_key(key: str) -> bool:
    """检查某个键是否有翻译"""
    return key in _current


def add_translation(key: str, value: str) -> None:
    """动态添加翻译（运行时）"""
    _current[key] = value


# 启动时自动加载系统语言
load_language()
