# -*- coding: utf-8 -*-
"""主题日记：自动记录群消息，支持按日期/关键词/主题查询（移植自 rqhbot theme_diary）"""

import json
import os
import re
from datetime import datetime

from .config import DIARY_DIR

# 日记查询命令前缀（必须以此开头才视为日记命令，避免与「爬」「查词」等抢词）
QUERY_PREFIXES = ("日记", "查日记", "搜索日记", "日记主题")

# 主题判定关键词
TOPIC_KEYWORDS = {
    "AI与模型": ("模型", "ai", "AI", "gpt", "GPT", "qwen", "Qwen", "deepseek", "DeepSeek", "api", "API"),
    "代码与开发": ("代码", "bug", "Bug", "插件", "函数", "报错", "修复", "开发", "github", "GitHub"),
    "群聊日常": ("早", "晚安", "吃", "睡", "摸鱼", "聊天", "日常"),
    "图片与表情": ("[图片", "[表情", "表情包", "骰子", "猜拳", "戳一戳"),
}

# 日记帮助文本
HELP_TEXT = (
    "📘 主题日记帮助：\n"
    "日记 - 查看最近3天日记\n"
    "日记 YYYY-MM-DD - 按日期查看（如 日记 2026-09-28）\n"
    "查日记 [YYYY-MM-DD] - 同上\n"
    "搜索日记 关键词 - 全文搜索日记\n"
    "日记主题 - 列出所有主题\n"
    "日记主题 主题名 - 按主题查看\n"
    "日记帮助 - 显示本帮助"
)


def record(text: str, group_id: str, user_id: str, username: str) -> None:
    """记录一条群消息进日记，任何情况下都不抛异常"""
    try:
        text = (text or "").strip()
        if not text or not group_id:
            return
        # 查询命令本身不写入日记（与源码行为一致）
        if text.startswith(QUERY_PREFIXES):
            return
        now = datetime.now()
        path = os.path.join(DIARY_DIR, str(group_id), now.strftime("%Y-%m-%d") + ".json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            data = {}
        entries = data.setdefault("entries", [])
        entries.append({
            "time": now.strftime("%H:%M:%S"),
            "topic": _detect_topic(text),
            "user_id": str(user_id or ""),
            "username": str(username or user_id or ""),
            "text": text,
        })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        return  # 记录失败不影响主流程


async def handle(text: str, group_id: str, user_id: str, username: str,
                 reply_image=None) -> str | None:
    """处理日记查询命令：非日记命令返回 None，需要回复返回字符串"""
    text = (text or "").strip()
    if not text.startswith(QUERY_PREFIXES):
        return None
    try:
        # 按长前缀优先分派，参数取对应命令前缀之后的内容
        if text.startswith("搜索日记"):
            return _search(group_id, text[len("搜索日记"):].strip())
        if text.startswith("日记主题"):
            return _search_by_topic(group_id, text[len("日记主题"):].strip())
        if text.startswith("查日记"):
            return _read_by_date(group_id, text[len("查日记"):].strip())
        # 其余为「日记」开头：帮助或按日期查看
        arg = text[len("日记"):].strip()
        if arg in ("帮助", "help", "Help", "HELP"):
            return HELP_TEXT
        return _read_by_date(group_id, arg)
    except Exception as e:
        return f"查询日记时出错: {e}"


# ---------------------------------------------------------------------------
# 内部辅助
# ---------------------------------------------------------------------------
def _detect_topic(content: str) -> str:
    """按关键词判定消息主题"""
    for topic, keywords in TOPIC_KEYWORDS.items():
        if any(keyword in content for keyword in keywords):
            return topic
    if re.search(r"https?://|www\.", content, re.IGNORECASE):
        return "链接与资料"
    if re.search(r"[?？]$|怎么|为什么|如何|能不能|可不可以", content):
        return "问题与讨论"
    return "未分类记录"


def _list_files(group_id: str):
    """列出该群所有日记文件，按日期倒序"""
    directory = os.path.join(DIARY_DIR, str(group_id or ""))
    if not os.path.isdir(directory):
        return []
    files = [os.path.join(directory, name) for name in os.listdir(directory)
             if name.endswith(".json")]
    files.sort(key=lambda p: os.path.splitext(os.path.basename(p))[0], reverse=True)
    return files


def _load_entries(path: str):
    """读取单个日记文件的条目列表"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return []
    if isinstance(data, dict):
        entries = data.get("entries", [])
        return entries if isinstance(entries, list) else []
    return []


def _entry_line(entry) -> str:
    """条目转单行展示文本"""
    text = str(entry.get("text", "")).replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", " ").strip()
    return f"[{entry.get('time', '')}] {entry.get('username', '')}：{text}"


def _format_day(date_str: str, entries) -> str:
    """把一天的条目按主题分组渲染"""
    lines = [f"📅 {date_str}"]
    current = None
    for entry in entries:
        topic = str(entry.get("topic", "") or "未分类记录")
        if topic != current:
            lines.append(f"## {topic}")
            current = topic
        lines.append(_entry_line(entry))
    return "\n".join(lines)


def _clip(content: str, limit: int) -> str:
    """超长截断"""
    if len(content) > limit:
        return content[:limit] + "\n...(内容过长，已截断)"
    return content


def _read_by_date(group_id: str, date_str: str) -> str:
    """按日期读取日记；无日期则返回最近 3 天摘要"""
    if not date_str:
        blocks = []
        for path in _list_files(group_id)[:3]:
            entries = _load_entries(path)
            if not entries:
                continue
            date = os.path.splitext(os.path.basename(path))[0]
            blocks.append(_clip(_format_day(date, entries), 800))
        if not blocks:
            return "暂无日记记录"
        return _clip("\n\n".join(blocks), 1500)

    # 解析日期
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return "❌ 日期格式错误，应为 YYYY-MM-DD（如 2026-08-27）"
    date = target.strftime("%Y-%m-%d")
    path = os.path.join(DIARY_DIR, str(group_id or ""), date + ".json")
    entries = _load_entries(path)
    if not entries:
        return f"❌ 未找到 {date} 的日记"
    return _clip(_format_day(date, entries), 1500)


def _search(group_id: str, keyword: str) -> str:
    """全文搜索日记"""
    if not keyword:
        return "请提供搜索关键词，如：搜索日记 bug"

    matches = []  # (日期, 展示行)
    for path in _list_files(group_id):
        date = os.path.splitext(os.path.basename(path))[0]
        for entry in _load_entries(path):
            body = str(entry.get("text", ""))
            name = str(entry.get("username", ""))
            if keyword in body or keyword in name:
                matches.append((date, _entry_line(entry)))
                if len(matches) >= 20:
                    break
        if len(matches) >= 20:
            break

    if not matches:
        return f"🔍 未找到包含「{keyword}」的日记记录"

    lines = [f"🔍 搜索「{keyword}」找到 {len(matches)} 条记录："]
    prev_date = None
    for date, line in matches:
        if date != prev_date:
            lines.append(f"\n📅 {date}")
            prev_date = date
        lines.append(f"   {line}")
    return _clip("\n".join(lines), 1500)


def _search_by_topic(group_id: str, topic: str) -> str:
    """按主题搜索日记"""
    files = _list_files(group_id)

    if not topic:
        # 未指定主题则列出全部可用主题
        topics = set()
        for path in files:
            for entry in _load_entries(path):
                t = str(entry.get("topic", "")).strip()
                if t:
                    topics.add(t)
        if not topics:
            return "暂无主题记录"
        return "📚 可用主题：\n" + "\n".join(f"- {t}" for t in sorted(topics))

    matches = []
    for path in files:
        date = os.path.splitext(os.path.basename(path))[0]
        for entry in _load_entries(path):
            if str(entry.get("topic", "")).strip() == topic:
                matches.append((date, _entry_line(entry)))
                if len(matches) >= 20:
                    break
        if len(matches) >= 20:
            break

    if not matches:
        return f"📚 未找到主题「{topic}」的日记记录"

    lines = [f"📚 主题「{topic}」找到 {len(matches)} 条记录："]
    prev_date = None
    for date, line in matches:
        if date != prev_date:
            lines.append(f"\n📅 {date}")
            prev_date = date
        lines.append(f"   {line}")
    return _clip("\n".join(lines), 1500)
