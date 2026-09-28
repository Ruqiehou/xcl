# -*- coding: utf-8 -*-
"""发言统计：日榜/周榜/月榜/年榜"""

import json
import os
from collections import Counter
from datetime import datetime, timedelta

from .config import SPEECH_DIR


class SpeechStats:
    """发言统计管理器"""

    def record_speech(self, group_id: str, user_id: str, username: str):
        """记录一次发言"""
        now = datetime.now()
        day_file = os.path.join(SPEECH_DIR, group_id, now.strftime("%Y-%m-%d.json"))
        os.makedirs(os.path.dirname(day_file), exist_ok=True)

        try:
            with open(day_file, "r", encoding="utf-8") as f:
                day = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            day = {"users": {}}

        day.setdefault("users", {})
        u = day["users"].setdefault(user_id, {"count": 0, "username": username})
        u["count"] += 1
        u["username"] = username
        with open(day_file, "w", encoding="utf-8") as f:
            json.dump(day, f, ensure_ascii=False, indent=2)

    def handle_command(self, text, group_id, user_id):
        """处理发言统计命令"""
        if text == "注册":
            return "已注册，发言数据自动统计。"
        if text == "我的发言":
            return self._speech_user(group_id, user_id, days=30)
        days = {"发言日榜": 1, "发言周榜": 7, "发言月榜": 30, "发言年榜": 365}.get(text, 30)
        return self._speech_rank(group_id, days)

    def _speech_agg(self, group_id, days):
        counts = Counter()
        names = {}
        today = datetime.now()
        for i in range(days):
            day = today - timedelta(days=i)
            path = os.path.join(SPEECH_DIR, group_id, day.strftime("%Y-%m-%d.json"))
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                continue
            for uid, u in data.get("users", {}).items():
                counts[uid] += u.get("count", 0)
                names[uid] = u.get("username", uid)
        return counts, names

    def _speech_user(self, group_id, user_id, days):
        counts, _ = self._speech_agg(group_id, days)
        return f"你最近{days}天共发言 {counts.get(user_id, 0)} 次。"

    def _speech_rank(self, group_id, days):
        counts, names = self._speech_agg(group_id, days)
        if not counts:
            return "暂无发言数据。"
        medals = {0: "🥇", 1: "🥈", 2: "🥉"}
        lines = [f"🏆 发言排行（近{days}天）🏆"]
        for i, (uid, cnt) in enumerate(counts.most_common(10)):
            medal = medals.get(i, "")
            lines.append(f"{medal}{i+1}. {names.get(uid, uid)}：{cnt}次")
        return "\n".join(lines)
