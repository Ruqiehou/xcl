# -*- coding: utf-8 -*-
"""全局路径常量与配置"""

import json
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
QNA_DIR = os.path.join(DATA_DIR, "qn")
SIGNIN_DIR = os.path.join(DATA_DIR, "signin")
SPEECH_DIR = os.path.join(DATA_DIR, "speech")
SUMMARY_DATA_DIR = os.path.join(DATA_DIR, "summary")
DICTIONARY_PATH = os.path.join(DATA_DIR, "csmsword.json")

for _d in (DATA_DIR, QNA_DIR, SIGNIN_DIR, SPEECH_DIR, SUMMARY_DATA_DIR):
    os.makedirs(_d, exist_ok=True)

# 管理员 openid 列表（问答管理命令使用）
ADMIN_IDS: set = set()

# botpy 消息中 @ 机器人的文本形式
MENTION_PATTERN = re.compile(r"<@![0-9a-zA-Z_\-]+>")
