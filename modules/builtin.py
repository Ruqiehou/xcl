# -*- coding: utf-8 -*-
"""内置基础指令：ping / 帮助 / echo / 运势"""

import random

HELP_TEXT = (
    "我是 masu，整合版群机器人，可用功能：\n"
    "【基础】ping / 帮助 / echo / 运势\n"
    "【群总结】群总结 / 群总结 7天 / 群总结 用户 <openid> / 群总结帮助\n"
    "【签到】签到 / 我的积分 / 我的信息 / 积分排行 / 积分商城 / 兑换<n> / 设置名字<名字> / 发言排行 / 查发言<id>\n"
    "【发言】注册 / 我的发言 / 发言日榜 / 发言周榜 / 发言月榜 / 发言季榜 / 发言年榜\n"
    "【发言】历史日榜 / 历史周榜 / 历史月榜 / 历史年榜 / 设置用户名 / 查询发言\n"
    "【问答】问答帮助（精确问/模糊问/修改/删问答/列出/清空）\n"
    "【工具】查词<词> / 粗查<词> / 天气<城市> / 新闻 / 定位<ip> / 转写<数字> / 爬<关键词>"
)

_FORTUNE_LEVELS = ["大凶", "凶", "小凶", "平", "小吉", "中吉", "吉", "大吉"]
_FORTUNE_COLORS = ["红色", "金色", "蓝色", "绿色", "紫色", "白色", "黑色", "橙色"]
_FORTUNE_ADVICES = [
    "宜早睡早起，保持好心情", "宜大胆尝试新事物", "宜与朋友聚餐，增进感情",
    "宜运动健身，元气满满", "忌冲动消费，理性购物", "忌熬夜刷手机，注意休息",
    "忌与人争执，退一步海阔天空", "宜静心阅读，充实自己",
]

_HELP_ALIASES = ("/help", "/帮助", "帮助", "指令", "指南")
_FORTUNE_ALIASES = ("/运势", "/我的运势", "/今日运势", "运势", "今日运势", "我的运势")


def daily_fortune():
    return (f"🔮 今日运势\n────────\n运势：{random.choice(_FORTUNE_LEVELS)}\n"
            f"幸运数字：{random.randint(1, 99)}\n幸运颜色：{random.choice(_FORTUNE_COLORS)}\n"
            f"今日建议：{random.choice(_FORTUNE_ADVICES)}")


def owns(text):
    """是否属于内置指令（供分发器判断）"""
    return (text in ("/ping", "ping") or text in _HELP_ALIASES
            or text.startswith("/echo ") or text in _FORTUNE_ALIASES)


def handle_command(text):
    """内置指令处理；返回回复文本，未命中返回 None"""
    if text in ("/ping", "ping"):
        return "pong！"
    if text in _HELP_ALIASES:
        return HELP_TEXT
    if text.startswith("/echo "):
        return text[6:]
    if text in _FORTUNE_ALIASES:
        return daily_fortune()
    return None
