# -*- coding: utf-8 -*-
"""
统一使用官方 qq-botpy SDK 收发消息，身份标识使用 openid（member_openid）。
所有数据存储在 data/ 目录，功能按模块拆分在 modules/ 下。
"""

import asyncio
import json
import os
import random

import botpy
from botpy import logging
from botpy.connection import ConnectionState
from botpy.message import GroupMessage, C2CMessage

from modules.config import DICTIONARY_PATH, ADMIN_IDS, MENTION_PATTERN
from modules.qna import AnswerManager
from modules.summary import GroupSummary
from modules.speech import SpeechStats
from modules.signin import SignInSystem
from modules.tools import ToolCommands

logging.bot_log = True
logger = logging.get_logger(__name__)

# qq-botpy 1.2.1 未内置「群全量消息（免@）」事件解析，这里补上。
# 平台需在群设置中允许机器人接收全部消息，事件才会推送（Intent 同为 1<<25）。
def _parse_group_message_create(self, payload):
    _message = GroupMessage(self.api, payload.get("id", None), payload.get("d", {}))
    self._dispatch("group_message_create", _message)

ConnectionState.parse_group_message_create = _parse_group_message_create


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------
def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _daily_fortune():
    levels = ["大凶", "凶", "小凶", "平", "小吉", "中吉", "吉", "大吉"]
    colors = ["红色", "金色", "蓝色", "绿色", "紫色", "白色", "黑色", "橙色"]
    advices = [
        "宜早睡早起，保持好心情", "宜大胆尝试新事物", "宜与朋友聚餐，增进感情",
        "宜运动健身，元气满满", "忌冲动消费，理性购物", "忌熬夜刷手机，注意休息",
        "忌与人争执，退一步海阔天空", "宜静心阅读，充实自己",
    ]
    return (f"🔮 今日运势\n────────\n运势：{random.choice(levels)}\n"
            f"幸运数字：{random.randint(1, 99)}\n幸运颜色：{random.choice(colors)}\n"
            f"今日建议：{random.choice(advices)}")


HELP_TEXT = (
    "我是 masu，整合版群机器人，可用功能：\n"
    "【基础】ping / 帮助 / echo / 运势\n"
    "【群总结】群总结 / 群总结 7天 / 群总结 用户 <openid> / 群总结帮助\n"
    "【签到】签到 / 我的积分 / 我的信息 / 积分排行 / 积分商城 / 兑换<n> / 设置名字<名字> / 发言排行 / 查发言<id>\n"
    "【发言】注册 / 我的发言 / 发言日榜 / 发言周榜 / 发言月榜 / 发言年榜\n"
    "【问答】问答帮助（精确问/模糊问/修改/删问答/列出/清空）\n"
    "【工具】查词<词> / 粗查<词> / 天气<城市> / 新闻 / 定位<ip> / 转写<数字> / 爬<关键词>"
)


# ---------------------------------------------------------------------------
# 机器人类
# ---------------------------------------------------------------------------
class MyClient(botpy.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reply_seq = 0
        self._seq_lock = asyncio.Lock()

        # 加载词典
        self.dictionary = _load_json(DICTIONARY_PATH)

        # 初始化各功能模块
        self.summary = GroupSummary()
        self.speech = SpeechStats()
        self.signin = SignInSystem(self.dictionary, _daily_fortune)
        self.qna = AnswerManager()
        self.tools = ToolCommands(self.dictionary)

    async def _reply(self, message, content: str):
        async with self._seq_lock:
            self._reply_seq += 1
            seq = self._reply_seq
        await message.reply(content=content, msg_seq=seq)

    @staticmethod
    def _strip_mention(content: str) -> str:
        return MENTION_PATTERN.sub("", content or "").strip()

    async def on_ready(self):
        logger.info(f"机器人「{self.robot.name}」启动成功！")

    # ---------------- 群消息 ----------------
    async def on_group_at_message_create(self, message: GroupMessage):
        await self._handle_group(message)

    async def on_group_message_create(self, message: GroupMessage):
        """群全量消息（免@）"""
        await self._handle_group(message)

    async def _handle_group(self, message: GroupMessage):
        content = message.content or ""
        text = self._strip_mention(content)
        if not text:
            return

        group_id = str(getattr(message, "group_openid", "") or "")
        user_id = str(getattr(message.author, "member_openid", "") or "")
        username = "User_" + (user_id[-6:] if user_id else "unknown")

        # 记录发言（各模块各自记录）
        try:
            self.summary.record_speech(group_id, user_id, username, text)
            self.speech.record_speech(group_id, user_id, username)
            self.signin.record_speech(user_id, username)
        except Exception as e:
            logger.warning(f"记录发言失败: {e}")

        reply = await self._dispatch_group(text, group_id, user_id, username)
        if reply is not None:
            await self._reply(message, reply)

    async def _dispatch_group(self, text, group_id, user_id, username):
        """返回要回复的文本；无回复返回 None"""
        # 基础指令
        handled = self._built_in(text)
        if handled is not None:
            return handled

        # 群总结
        if text == "群总结帮助" or text.startswith("群总结"):
            return self.summary.handle_command(group_id, text)

        # 签到积分
        if text in ("签到", "签到帮助", "我的积分", "我的信息", "积分排行", "积分商城", "登记发言") \
                or text.startswith("兑换") or text.startswith("设置名字") \
                or text == "发言排行" or text.startswith("查发言"):
            return self.signin.handle_command(text, user_id, username, group_id)

        # 发言统计
        if text in ("注册", "我的发言", "发言日榜", "发言周榜", "发言月榜", "发言年榜"):
            return self.speech.handle_command(text, group_id, user_id)

        # 问答管理
        if text.startswith(("精确问", "模糊问")) or text.startswith("修改") \
                or text.startswith("删问答") or text.startswith("列出") \
                or text.startswith("清空所有问答") or text == "问答帮助":
            return self._qna_command(text, user_id)

        # 工具
        if text.startswith("查词"):
            return self.tools.lookup(text[2:])
        if text.startswith("粗查"):
            return self.tools.coarse_lookup(text[2:])
        if text.startswith("天气"):
            return await self.tools.weather_cmd(text[2:])
        if text == "新闻":
            return await self.tools.news_cmd()
        if text.startswith("定位"):
            return self.tools.ip_cmd(text[2:])
        if text.startswith("转写"):
            return self.tools.zhuanxie_cmd(text[2:])
        if text.startswith("爬"):
            return await self.tools.search_cmd(text[1:])

        # 本地问答自动应答
        answer = self.qna.search(text)
        if answer:
            return answer

        return None  # 未知指令保持静默

    # ---------------- 内置指令 ----------------
    def _built_in(self, text):
        if text in ("/ping", "ping"):
            return "pong！"
        if text in ("/help", "/帮助", "帮助", "指令"):
            return HELP_TEXT
        if text.startswith("/echo "):
            return text[6:]
        if text in ("/运势", "/我的运势", "/今日运势", "运势", "今日运势", "我的运势"):
            return _daily_fortune()
        if text in ("指南",):
            return HELP_TEXT
        return None

    # ---------------- 问答管理 ----------------
    def _qna_command(self, text, user_id):
        is_admin = user_id in ADMIN_IDS
        if text == "问答帮助":
            return ("问答帮助：\n精确问 问题 答 答案（管理员）\n模糊问 问题 答 答案（管理员）\n"
                    "修改 原问题 答 新答案（管理员）\n删问答 问题（管理员）\n列出/清空（管理员）")
        if text.startswith("精确问") or text.startswith("模糊问"):
            if not is_admin:
                return "你没有权限添加问答"
            import re
            m = re.match(r"^(精确问|模糊问) (.+?) 答 (.+)$", text, re.DOTALL)
            if not m:
                return "格式：精确问/模糊问 问题 答 答案"
            kind, q, a = m.groups()
            self.qna.add_answer(q, a, fuzzy=(kind == "模糊问"))
            return f"问答添加成功：\n问：{q.strip()}\n答：{a.strip()}"
        if text.startswith("修改"):
            if not is_admin:
                return "你没有权限修改问答"
            parts = text[2:].split("答", 1)
            if len(parts) == 2:
                if self.qna.update_answer(parts[0].strip(), parts[1].strip()):
                    return f"修改成功：{parts[0].strip()}"
                return f"未找到问题：{parts[0].strip()}"
            return "格式：修改 原问题 答 新答案"
        if text.startswith("删问答"):
            if not is_admin:
                return "你没有权限删除问答"
            q = text[3:].strip()
            if not q:
                return "格式：删问答 问题"
            return "删除成功" if self.qna.delete_answer(q) else "未找到该问题"
        if text.startswith("清空所有问答"):
            if not is_admin:
                return "你没有权限清空问答"
            self.qna.clear_all_answers()
            return "问答已清空"
        if text.startswith("列出"):
            if not is_admin:
                return "你没有权限查看问答"
            data = self.qna.all_data()
            if not data:
                return "还没有任何问答记录"
            return "当前问答（智能抽查10条）：\n" + "\n".join(f"问：{q}\n答：{a}" for q, a in
                                                                 list(data.items())[:10])
        return None

    # ---------------- 私聊 ----------------
    async def on_c2c_message_create(self, message: C2CMessage):
        content = message.content or ""
        text = content.strip()
        if not text:
            return
        reply = self._built_in(text)
        if reply is None:
            reply = "私聊仅支持：ping、帮助、echo、运势。群功能请在群内@我使用。"
        await self._reply(message, reply)


if __name__ == "__main__":
    import yaml

    config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    appid = config["appid"]
    secret = config["secret"]

    intents = botpy.Intents(public_messages=True)
    client = MyClient(intents=intents)
    client.run(appid=appid, secret=secret)
