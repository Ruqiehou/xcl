# -*- coding: utf-8 -*-
"""群总结：记录发言并生成报告"""

import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from .config import SUMMARY_DATA_DIR


class GroupSummary:
    """群总结管理器"""

    STOP_WORDS = {
        "的", "了", "是", "我", "你", "他", "她", "它", "和", "就", "都", "也", "很",
        "在", "有", "没", "不", "啊", "吗", "吧", "呢", "一个", "这个", "那个", "什么",
        "怎么", "为什么", "可以", "不是", "还是", "然后", "如果", "但是", "所以", "因为", "已经"
    }

    def record_speech(self, group_id: str, user_id: str, username: str, text: str):
        """记录一条发言"""
        now = datetime.now()
        row = {
            "time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "timestamp": int(now.timestamp()),
            "group_id": group_id,
            "user_id": user_id,
            "user_name": username,
            "text": text,
        }
        with open(os.path.join(SUMMARY_DATA_DIR, f"{now.strftime('%Y-%m-%d')}.jsonl"),
                  "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _iter_records(self, group_id, days):
        today = datetime.now().date()
        start = today - timedelta(days=days - 1)
        for i in range(days):
            day = start + timedelta(days=i)
            path = os.path.join(SUMMARY_DATA_DIR, f"{day.strftime('%Y-%m-%d')}.jsonl")
            if not os.path.exists(path):
                continue
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                    except Exception:
                        continue
                    if str(row.get("group_id")) == group_id:
                        yield row

    def handle_command(self, group_id, text):
        """处理群总结命令"""
        if text == "群总结帮助":
            return "群总结命令：\n群总结 - 今日\n群总结 7天 - 最近7天\n群总结 用户 <openid> - 指定用户报告\n群总结帮助 - 说明"
        if text.startswith("群总结"):
            args = text.split()
            if len(args) >= 3 and args[1] == "用户":
                return self._user_report(group_id, args[2], days=7)
            days = 1
            if len(args) >= 2:
                v = args[1]
                if v not in ("今日", "今天", "日"):
                    m = re.search(r"(\d+)", v)
                    if m:
                        days = max(1, min(int(m.group(1)), 30))
            return self._group_report(group_id, days)
        return None

    def _group_report(self, group_id, days):
        records = list(self._iter_records(group_id, days))
        period = "今日" if days == 1 else f"最近{days}天"
        if not records:
            return f"📊 群总结报告（{period}）\n暂无可总结的用户消息。"
        stats = defaultdict(lambda: {"name": "", "count": 0, "chars": 0, "messages": []})
        word_c = Counter()
        for row in records:
            text = str(row.get("text", "")).strip()
            uid = str(row.get("user_id", ""))
            stats[uid]["name"] = str(row.get("user_name", uid))
            stats[uid]["count"] += 1
            stats[uid]["chars"] += len(text)
            stats[uid]["messages"].append(text)
            word_c.update(self._extract_words(text))
        top = sorted(stats.items(), key=lambda x: x[1]["count"], reverse=True)[:5]
        lines = [f"📊 群总结报告（{period}）", f"群号：{group_id}",
                 f"消息数：{len(records)} 条", f"参与用户：{len(stats)} 人", "",
                 "🏆 发言榜："]
        for idx, (uid, s) in enumerate(top, 1):
            avg = s["chars"] / max(s["count"], 1)
            lines.append(f"{idx}. {s['name']}（{uid}）：{s['count']}条，均长{avg:.1f}字")
        top_words = "、".join(w for w, _ in word_c.most_common(12)) or "暂无"
        lines += ["", f"高频词：{top_words}"]
        return "\n".join(lines)

    def _user_report(self, group_id, target_uid, days):
        records = [r for r in self._iter_records(group_id, days) if str(r.get("user_id")) == target_uid]
        if not records:
            return f"📊 用户风格报告\n用户 {target_uid} 最近{days}天暂无记录。"
        name = str(records[-1].get("user_name", target_uid))
        msgs = [str(r.get("text", "")).strip() for r in records if str(r.get("text", "")).strip()]
        word_c = Counter()
        for m in msgs:
            word_c.update(self._extract_words(m))
        return (f"📊 用户风格报告\n用户：{name}（{target_uid}）\n范围：最近{days}天\n"
                f"发言数：{len(msgs)} 条\n高频词：{'、'.join(w for w, _ in word_c.most_common(12)) or '暂无'}")

    def _extract_words(self, text):
        words = re.findall(r"[A-Za-z0-9_]{2,}|[\u4e00-\u9fff]{2,4}", text)
        return [w for w in words if w not in self.STOP_WORDS and not w.isdigit()]
