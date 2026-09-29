# -*- coding: utf-8 -*-
"""
统一使用官方 qq-botpy SDK 收发消息，身份标识使用 openid（member_openid）。
本文件只负责：连接事件、消息解析、发言记录、命令分发与回复。
具体功能实现全部在 modules/ 下，新增功能只需在 COMMAND_HANDLERS 中注册。
"""

import asyncio
import inspect

import botpy
from botpy import logging
from botpy.message import GroupMessage, C2CMessage

from modules import builtin
from modules.config import (DICTIONARY_PATH, MENTION_PATTERN, MsgCtx,
                            load_bot_config, load_json)
from modules.patches import apply_group_message_patch
from modules.qna import AnswerManager
from modules.summary import GroupSummary
from modules.speech import SpeechStats
from modules.signin import SignInSystem
from modules.tools import ToolCommands

logging.bot_log = True
logger = logging.get_logger(__name__)

apply_group_message_patch()


class MyClient(botpy.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reply_seq = 0
        self._seq_lock = asyncio.Lock()

        self.dictionary = load_json(DICTIONARY_PATH)

        # 各功能模块
        self.summary = GroupSummary()
        self.speech = SpeechStats()
        self.signin = SignInSystem(self.dictionary, builtin.daily_fortune)
        self.qna = AnswerManager()
        self.tools = ToolCommands(self.dictionary)

        # 命令分发表：按顺序匹配，模块通过 owns(text) 声明归属，
        # handle(text, ctx) 返回回复文本（无回复返回 None）。
        self.command_handlers = [
            self.summary, self.signin, self.speech, self.qna, self.tools,
        ]

    # ---------------- 回复 ----------------
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
        text = self._strip_mention(message.content or "")
        if not text:
            return

        user_id = str(getattr(message.author, "member_openid", "") or "")
        ctx = MsgCtx(
            group_id=str(getattr(message, "group_openid", "") or ""),
            user_id=user_id,
            username="User_" + (user_id[-6:] if user_id else "unknown"),
        )

        self._record_speech(ctx, text)

        reply = await self._dispatch(text, ctx)
        if reply is not None:
            await self._reply(message, reply)

    def _record_speech(self, ctx, text):
        """所有模块各自记录发言"""
        try:
            self.summary.record_speech(ctx.group_id, ctx.user_id, ctx.username, text)
            self.speech.record_speech(ctx.group_id, ctx.user_id, ctx.username)
            self.signin.record_speech(ctx.user_id, ctx.username)
        except Exception as e:
            logger.warning(f"记录发言失败: {e}")

    async def _dispatch(self, text, ctx):
        """返回要回复的文本；无回复返回 None"""
        if builtin.owns(text):
            return builtin.handle_command(text)

        for handler in self.command_handlers:
            if not handler.owns(text):
                continue
            result = handler.handle(text, ctx)
            if inspect.isawaitable(result):
                result = await result
            if result is not None:
                return result

        # 未命中任何命令时尝试本地问答自动应答
        return self.qna.search(text)

    # ---------------- 私聊 ----------------
    async def on_c2c_message_create(self, message: C2CMessage):
        text = (message.content or "").strip()
        if not text:
            return
        reply = builtin.handle_command(text)
        if reply is None:
            reply = "私聊仅支持：ping、帮助、echo、运势。群功能请在群内@我使用。"
        await self._reply(message, reply)


if __name__ == "__main__":
    appid, secret = load_bot_config()
    client = MyClient(intents=botpy.Intents(public_messages=True))
    client.run(appid=appid, secret=secret)
