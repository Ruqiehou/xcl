# -*- coding: utf-8 -*-
"""发言统计：日榜/周榜/月榜/季榜/年榜、历史榜、设置用户名、查询发言"""

import json
import os
from collections import Counter
from datetime import datetime, timedelta

from .config import SPEECH_DIR

# 自定义用户名存储（与 data/speech/ 下各群目录并列的 JSON 文件）
USERNAME_FILE = os.path.join(SPEECH_DIR, "usernames.json")

# 榜单展示条数
TOP_N = 10

# 星期展示（下标对应 weekday()）
_WEEKDAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


class SpeechStats:
    """发言统计管理器"""

    COMMANDS = ("注册", "我的发言", "发言日榜", "发言周榜", "发言月榜", "发言年榜")
    PREFIX_COMMANDS = ("历史日榜", "历史周榜", "历史月榜", "历史年榜",
                       "设置用户名", "查询发言")
    EXTRA_COMMANDS = ("发言季榜", "赛季榜")

    # ==================== 基础读写 ====================

    def record(self, ctx, text: str = ""):
        """统一发言记录接口（供 bot.py 注册表调用）"""
        self.record_speech(ctx.group_id, ctx.user_id, ctx.username)

    def record_speech(self, group_id: str, user_id: str, username: str):
        """记录一次发言"""
        # 用户设置过自定义用户名时，以自定义名字为准
        username = self._load_usernames().get(user_id) or username
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

    def _load_usernames(self):
        """读取自定义用户名映射 {user_id: 用户名}"""
        try:
            with open(USERNAME_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_usernames(self, data):
        """保存自定义用户名映射"""
        os.makedirs(SPEECH_DIR, exist_ok=True)
        with open(USERNAME_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _list_day_files(self, group_id):
        """列出该群所有日文件名（升序，文件名形如 2026-09-28.json）"""
        group_dir = os.path.join(SPEECH_DIR, group_id)
        try:
            files = [f for f in os.listdir(group_dir) if f.endswith(".json")]
        except (FileNotFoundError, NotADirectoryError):
            return []
        return sorted(files)

    def _read_day(self, group_id, filename):
        """读取单个日文件，失败返回空结构"""
        path = os.path.join(SPEECH_DIR, group_id, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, NotADirectoryError, IsADirectoryError):
            return {}
        return data if isinstance(data, dict) else {}

    def _agg_files(self, group_id, filenames):
        """按文件名列表聚合发言数，返回 (Counter, {user_id: 显示名})"""
        counts = Counter()
        names = {}
        usernames = self._load_usernames()
        for filename in filenames:
            day = self._read_day(group_id, filename)
            for uid, u in day.get("users", {}).items():
                if not isinstance(u, dict):
                    continue
                counts[uid] += u.get("count", 0)
                # 展示名优先级：自定义用户名 > 日文件记录名 > 用户ID
                names[uid] = usernames.get(uid) or u.get("username") or uid
        return counts, names

    def _agg_dates(self, group_id, date_strs):
        """聚合指定日期（YYYY-MM-DD 列表）的日文件"""
        return self._agg_files(group_id, [f"{d}.json" for d in date_strs])

    def _agg_prefix(self, group_id, *prefixes):
        """按文件名前缀聚合（如 "2026-"、"2026-09-"），可传多个前缀"""
        files = [f for f in self._list_day_files(group_id) if f.startswith(prefixes)]
        return self._agg_files(group_id, files)

    # ==================== 命令入口 ====================

    def owns(self, text):
        return (text in self.COMMANDS or text in self.EXTRA_COMMANDS
                or text.startswith(self.PREFIX_COMMANDS))

    def handle(self, text, ctx):
        return self.handle_command(text, ctx.group_id, ctx.user_id)

    def handle_command(self, text, group_id, user_id):
        """处理发言统计命令；无法识别的命令返回 None"""
        text = (text or "").strip()
        # 原有命令
        if text == "注册":
            return "已注册，发言数据自动统计。"
        if text == "我的发言":
            return self._speech_user(group_id, user_id, days=30)
        days = {"发言日榜": 1, "发言周榜": 7, "发言月榜": 30, "发言年榜": 365}.get(text)
        if days is not None:
            return self._speech_rank(group_id, days)

        # 从 rqhspeech 移植的命令
        if text.startswith("历史日榜"):
            return self._history_daily(group_id, text)
        if text.startswith("历史周榜"):
            return self._history_weekly(group_id, text)
        if text.startswith("历史月榜"):
            return self._history_monthly(group_id, text)
        if text.startswith("历史年榜"):
            return self._history_yearly(group_id, text)
        if text in ("发言季榜", "赛季榜"):
            return self._season_rank(group_id)
        if text.startswith("设置用户名"):
            return self._set_username(group_id, user_id, text)
        if text.startswith("查询发言"):
            return self._query_user(group_id, text)
        return None

    # ==================== 原有命令 ====================

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
                names[uid] = self._load_usernames().get(uid) or u.get("username") or uid
        return counts, names

    def _speech_user(self, group_id, user_id, days):
        counts, _ = self._speech_agg(group_id, days)
        return f"你最近{days}天共发言 {counts.get(user_id, 0)} 次。"

    def _speech_rank(self, group_id, days):
        counts, names = self._speech_agg(group_id, days)
        if not counts:
            return "暂无发言数据。"
        return self._format_rank(counts, names, f"🏆 发言排行（近{days}天）🏆")

    def _format_rank(self, counts, names, header):
        """格式化排行榜文本：首行标题 + 奖牌 + 用户名 + 发言数"""
        medals = {0: "🥇", 1: "🥈", 2: "🥉"}
        lines = [header]
        for i, (uid, cnt) in enumerate(counts.most_common(TOP_N)):
            medal = medals.get(i, "")
            lines.append(f"{medal}{i+1}. {names.get(uid, uid)}：{cnt}次")
        return "\n".join(lines)

    # ==================== 历史榜命令 ====================

    def _history_daily(self, group_id, text):
        """历史日榜 YYYY-MM-DD"""
        parts = text.split()
        if len(parts) != 2:
            return "❌ 格式错误，请使用: 历史日榜 YYYY-MM-DD"
        date_str = parts[1]
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return "❌ 日期格式错误，请使用 YYYY-MM-DD 格式"

        counts, names = self._agg_dates(group_id, [date_str])
        if not counts:
            return f"📅 {date_str} 暂无发言记录"
        return self._format_rank(counts, names, f"🏆 {date_str} 发言日榜 🏆")

    def _parse_week(self, identifier):
        """
        解析历史周榜参数（YYYY-MM-DD 或 W数字）
        返回 (周一日期, 周日日期, 展示文本)；解析失败返回 (None, None, 错误信息)
        """
        if identifier[:1] in ("W", "w"):
            try:
                week_num = int(identifier[1:])
            except ValueError:
                return None, None, "周数格式错误"
            if week_num < 1 or week_num > 53:
                return None, None, "无效的周数"
            year = datetime.now().year
            try:
                first_day = datetime.strptime(f"{year}-W{week_num:02d}-1", "%Y-W%W-%w")
            except ValueError:
                return None, None, "周数格式错误"
            last_day = first_day + timedelta(days=6)
            info = f"{year}年第{week_num}周 ({first_day.strftime('%Y-%m-%d')} 至 {last_day.strftime('%Y-%m-%d')})"
            return first_day, last_day, info

        try:
            target = datetime.strptime(identifier, "%Y-%m-%d")
        except ValueError:
            return None, None, "日期格式错误，请使用 YYYY-MM-DD 格式"
        first_day = target - timedelta(days=target.weekday())
        last_day = first_day + timedelta(days=6)
        info = f"{first_day.strftime('%Y-%m-%d')} 至 {last_day.strftime('%Y-%m-%d')}"
        return first_day, last_day, info

    def _history_weekly(self, group_id, text):
        """历史周榜 YYYY-MM-DD 或 历史周榜 W数字（如 W06）"""
        parts = text.split()
        if len(parts) != 2:
            return "❌ 格式错误，请使用:\n历史周榜 YYYY-MM-DD（日期格式）\n或\n历史周榜 W数字（如 W06）"

        first_day, last_day, info = self._parse_week(parts[1])
        if first_day is None:
            return f"❌ {info}"

        dates = [(first_day + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        counts, names = self._agg_dates(group_id, dates)
        if not counts:
            return f"📅 {info} 暂无发言记录"
        return self._format_rank(counts, names, f"🏆 {info} 发言周榜 🏆")

    def _history_monthly(self, group_id, text):
        """历史月榜 YYYY-MM-DD（按该日期所在月份统计）"""
        parts = text.split()
        if len(parts) != 2:
            return "❌ 格式错误，请使用: 历史月榜 YYYY-MM-DD"
        try:
            target = datetime.strptime(parts[1], "%Y-%m-%d")
        except ValueError:
            return "❌ 日期格式错误，请使用 YYYY-MM-DD 格式"

        counts, names = self._agg_prefix(group_id, f"{target.year:04d}-{target.month:02d}-")
        if not counts:
            return f"{target.year}年{target.month}月 暂无发言记录"
        return self._format_rank(counts, names, f"🏆 {target.year}年{target.month}月 发言月榜 🏆")

    def _history_yearly(self, group_id, text):
        """历史年榜 YYYY"""
        parts = text.split()
        if len(parts) != 2:
            return "❌ 格式错误，请使用: 历史年榜 YYYY"
        try:
            year = int(parts[1])
            if year < 2000 or year > 9999:
                raise ValueError("年份超出范围")
        except ValueError:
            return "❌ 年份格式错误，请使用 YYYY 格式（如 2026）"

        counts, names = self._agg_prefix(group_id, f"{year:04d}-")
        if not counts:
            return f"{year}年 暂无发言记录"
        return self._format_rank(counts, names, f"🏆 {year}年 发言年榜 🏆")

    def _season_rank(self, group_id):
        """发言季榜 / 赛季榜：当前季度（春/夏/秋/冬）统计"""
        now = datetime.now()
        season = (now.month - 1) // 3 + 1
        season_name = {1: "春季", 2: "夏季", 3: "秋季", 4: "冬季"}[season]
        month_start = (season - 1) * 3 + 1
        prefixes = tuple(f"{now.year:04d}-{m:02d}-" for m in range(month_start, month_start + 3))
        counts, names = self._agg_prefix(group_id, *prefixes)
        if not counts:
            return "暂无发言记录"
        return self._format_rank(counts, names, f"🏆 发言季榜 ({now.year}年{season_name}) 🏆")

    # ==================== 设置用户名 / 查询发言 ====================

    def _latest_username(self, group_id, user_id):
        """在该群日文件中由新到旧查找用户记录的名字，找不到返回空串"""
        for filename in reversed(self._list_day_files(group_id)):
            users = self._read_day(group_id, filename).get("users", {})
            u = users.get(user_id)
            if isinstance(u, dict) and u.get("username"):
                return u["username"]
        return ""

    def _set_username(self, group_id, user_id, text):
        """设置用户名 <新名字>"""
        new_name = text[len("设置用户名"):].strip()
        if not new_name:
            return "❌ 请提供要设置的用户名\n格式：设置用户名 你的新名字"
        if len(new_name) > 20:
            return "❌ 用户名过长，请控制在20个字符以内"

        usernames = self._load_usernames()
        old_name = usernames.get(user_id) or self._latest_username(group_id, user_id) or user_id
        usernames[user_id] = new_name
        self._save_usernames(usernames)
        return f"✅ 用户名已更新：{old_name} → {new_name}"

    def _find_user(self, group_id, param):
        """按 openid 或用户名查找用户，返回 (user_id, 用户名) 或 None"""
        usernames = self._load_usernames()
        # openid 直接命中自定义名单
        if param in usernames:
            return param, usernames[param]
        # 自定义用户名反查 openid
        for uid, name in usernames.items():
            if name == param:
                return uid, name
        # 在本群日文件中按 openid 或记录名查找（由新到旧）
        for filename in reversed(self._list_day_files(group_id)):
            users = self._read_day(group_id, filename).get("users", {})
            if param in users:
                u = users[param]
                return param, usernames.get(param) or (u.get("username") if isinstance(u, dict) else "") or param
            for uid, u in users.items():
                if not isinstance(u, dict):
                    continue
                if u.get("username") == param:
                    return uid, usernames.get(uid) or u.get("username") or uid
        return None

    def _user_stats(self, group_id, user_id):
        """统计某用户在本群的今日/本周/本月/本年及累计发言数据"""
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        week_start = now - timedelta(days=now.weekday())
        week_start_str = week_start.strftime("%Y-%m-%d")
        week_key = f"{week_start.year}-W{week_start.isocalendar()[1]:02d}"
        month_prefix = now.strftime("%Y-%m")
        year_prefix = now.strftime("%Y") + "-"

        today = week = month = year = total = active_days = 0
        details = {}
        active_weeks = set()
        for filename in self._list_day_files(group_id):
            try:
                day_date = datetime.strptime(filename[:-5], "%Y-%m-%d")
            except ValueError:
                continue
            u = self._read_day(group_id, filename).get("users", {}).get(user_id)
            if not isinstance(u, dict):
                continue
            count = u.get("count", 0)
            if not count:
                continue
            total += count
            active_days += 1
            day_week_start = day_date - timedelta(days=day_date.weekday())
            active_weeks.add(f"{day_week_start.year}-W{day_week_start.isocalendar()[1]:02d}")
            if filename.startswith(year_prefix):
                year += count
            if filename.startswith(month_prefix):
                month += count
            date_str = filename[:-5]
            if week_start_str <= date_str <= today_str:
                week += count
                details[date_str] = count
            if date_str == today_str:
                today += count

        return {
            "today": today, "week": week, "month": month, "year": year,
            "total": total, "active_days": active_days, "active_weeks": len(active_weeks),
            "details": details, "week_key": week_key,
        }

    def _query_user(self, group_id, text):
        """查询发言 <openid 或 用户名>"""
        param = text[len("查询发言"):].strip()
        if not param:
            return "❌ 请提供查询参数\n格式：查询发言 openid 或 查询发言 用户名"

        found = self._find_user(group_id, param)
        if not found:
            return f"❌ 未找到用户 {param}"
        user_id, username = found
        s = self._user_stats(group_id, user_id)

        lines = [
            f"👤 用户 {username} ({user_id})",
            "",
            "📊 本群发言统计：",
            f"   今日发言: {s['today']} 条",
            f"   本周发言: {s['week']} 条",
            f"   本月发言: {s['month']} 条",
            f"   本年发言: {s['year']} 条",
            f"   活跃天数: {s['active_days']} 天",
        ]
        if s["details"]:
            lines.append("")
            lines.append(f"📅 本周每日明细 ({s['week_key']}):")
            for date_str in sorted(s["details"]):
                weekday = _WEEKDAYS[datetime.strptime(date_str, "%Y-%m-%d").weekday()]
                lines.append(f"   {date_str} ({weekday}): {s['details'][date_str]} 条")
        lines.append("")
        lines.append("📈 累计统计:")
        lines.append(f"   总发言数: {s['total']} 条")
        lines.append(f"   活跃周数: {s['active_weeks']} 周")
        return "\n".join(lines)
