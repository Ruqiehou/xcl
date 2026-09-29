# -*- coding: utf-8 -*-
"""全局路径常量与配置"""

import json
import os
import re
from collections import namedtuple

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
QNA_DIR = os.path.join(DATA_DIR, "qn")
SIGNIN_DIR = os.path.join(DATA_DIR, "signin")
SPEECH_DIR = os.path.join(DATA_DIR, "speech")
SUMMARY_DATA_DIR = os.path.join(DATA_DIR, "summary")
DIARY_DIR = os.path.join(DATA_DIR, "diary")
DICTIONARY_PATH = os.path.join(DATA_DIR, "csmsword.json")
ADMIN_IDS_PATH = os.path.join(DATA_DIR, "admins.json")

for _d in (DATA_DIR, QNA_DIR, SIGNIN_DIR, SPEECH_DIR, SUMMARY_DATA_DIR, DIARY_DIR):
    os.makedirs(_d, exist_ok=True)


def _load_admin_ids(path):
    """从 data/admins.json 读取管理员 openid 列表。

    文件格式为字符串数组，例如：["openid_xxx", "openid_yyy"]
    文件不存在时自动创建空模板；解析失败时返回空集合。
    """
    if not os.path.exists(path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
        except Exception:
            pass
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return {str(x) for x in data if x}
    except Exception:
        pass
    return set()


# 管理员 openid 集合（问答管理命令使用），来源：data/admins.json
ADMIN_IDS: set = _load_admin_ids(ADMIN_IDS_PATH)

# botpy 消息中 @ 机器人的文本形式
MENTION_PATTERN = re.compile(r"<@![0-9a-zA-Z_\-]+>")

# 消息上下文：群 openid、用户 openid、展示用用户名。各功能模块统一接收。
MsgCtx = namedtuple("MsgCtx", "group_id user_id username")

# 机器人登录配置（config.yaml 位于项目根目录）
BOT_CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")


def load_json(path, default=None):
    """读取 JSON 文件，失败返回 default（默认空 dict）"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception:
        return {} if default is None else default


def load_bot_config(path=BOT_CONFIG_PATH):
    """读取 config.yaml 中的 appid/secret。"""
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    return cfg["appid"], cfg["secret"]
