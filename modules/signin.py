# -*- coding: utf-8 -*-
"""签到积分系统"""

import json
import os
import random
from datetime import datetime

from .config import SIGNIN_DIR


class SignInSystem:
    """签到积分管理器"""

    SHOP = {
        "2": {"name": "专属称号", "price": 50000, "desc": "随机抽取一个称号"},
        "3": {"name": "运势查询", "price": 20000, "desc": "查看今日运势（文本）"},
        "4": {"name": "高级称号", "price": 200000, "desc": "抽取高级随机称号"},
        "5": {"name": "豪华礼包", "price": 1000000, "desc": "随机巨额积分奖励"},
        "6": {"name": "普通礼包", "price": 10000, "desc": "随机积分奖励"},
        "7": {"name": "随机减分", "price": 80000, "desc": "随机减少一位玩家积分"},
        "8": {"name": "随机加分", "price": 80000, "desc": "随机增加一位玩家积分"},
        "9": {"name": "积分清零", "price": 300000, "desc": "随机清零一位玩家积分"},
    }

    def __init__(self, dictionary: dict, daily_fortune_func):
        self.dictionary = dictionary
        self.daily_fortune = daily_fortune_func

    def record_speech(self, user_id: str, username: str):
        """记录发言（累计发言数和积分）"""
        sfile = os.path.join(SIGNIN_DIR, f"user_{user_id}.json")
        try:
            with open(sfile, "r", encoding="utf-8") as f:
                sdata = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            sdata = {}

        sdata.setdefault("points", 0)
        sdata.setdefault("last_sign_in", "")
        sdata.setdefault("status", "初来乍到")
        sdata.setdefault("message_count", 0)
        sdata.setdefault("username", username)
        sdata["message_count"] += 1
        sdata["points"] += random.randint(99, 10099)
        sdata["username"] = username
        with open(sfile, "w", encoding="utf-8") as f:
            json.dump(sdata, f, ensure_ascii=False, indent=2)

    def _load_user(self, user_id):
        sfile = os.path.join(SIGNIN_DIR, f"user_{user_id}.json")
        try:
            with open(sfile, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_user(self, user_id, data):
        with open(os.path.join(SIGNIN_DIR, f"user_{user_id}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def handle_command(self, text, user_id, username, group_id):
        """处理签到积分命令"""
        data = self._load_user(user_id)
        data.setdefault("points", 0)
        data.setdefault("last_sign_in", "")
        data.setdefault("status", "初来乍到")
        data.setdefault("message_count", 0)
        data["username"] = username

        if text == "签到":
            today = datetime.now().strftime('%Y-%m-%d')
            if data["last_sign_in"] == today:
                return "你今天已经签到过了"
            bonus = random.randint(88, 100000)
            data["points"] += bonus
            data["last_sign_in"] = today
            self._save_user(user_id, data)
            return f"签到成功！获得{bonus}积分\n用户名：{username}\n当前积分：{data['points']}\n发言：{data['message_count']}条"
        if text == "签到帮助":
            return ("签到帮助：\n签到-签到\n我的积分-查询积分\n我的信息-查询信息\n积分排行-积分榜\n"
                    "签到/设置名字<名字>-设置用户名\n积分商城-查看商品\n兑换<编号>-兑换商品\n发言排行/查发言<id>")
        if text == "我的积分":
            return f"用户名：{username}，当前积分：{data['points']}"
        if text == "我的信息":
            return (f"用户名：{username}\n积分：{data['points']}\n状态：{data['status']}\n"
                    f"上次签到：{data['last_sign_in']}\n发言：{data['message_count']}条")
        if text == "积分排行":
            return self._ranking()
        if text == "积分商城":
            return self._shop()
        if text.startswith("兑换"):
            return self._redeem(text[2:].strip(), user_id, username)
        if text.startswith("设置名字"):
            name = text[4:].strip()
            if not name:
                return "格式：设置名字 你的名字"
            old = data.get('username', '未设置')
            data['username'] = name
            self._save_user(user_id, data)
            return f"用户名已更新：{old} → {name}"
        if text == "发言排行":
            from .speech import SpeechStats
            return SpeechStats()._speech_rank(group_id, 30)
        if text.startswith("查发言"):
            target = text[3:].strip()
            if not target:
                return "格式：查发言 <openid>"
            tdata = self._load_user(target)
            return f"{tdata.get('username', target)} 共发言 {tdata.get('message_count', 0)} 次"
        if text == "登记发言":
            return f"已登记，当前发言：{data['message_count']}条"
        return None

    def _ranking(self):
        rows = []
        for fn in os.listdir(SIGNIN_DIR):
            if fn.startswith("user_") and fn.endswith(".json"):
                ud = self._load_user(fn[5:-5])
                rows.append((fn[5:-5], ud.get('points', 0)))
        rows.sort(key=lambda x: x[1], reverse=True)
        if not rows:
            return "暂无用户数据"
        lines = ["🏆 积分排行榜 🏆"]
        for i, (uid, pts) in enumerate(rows[:10]):
            ud = self._load_user(uid)
            name = ud.get('username', uid)
            lines.append(f"{i+1}. {name}：{pts}分")
        return "\n".join(lines)

    def _shop(self):
        lines = ["🏪 积分商城 🏪"]
        for iid, it in self.SHOP.items():
            lines.append(f"{iid}. {it['name']} - {it['price']}积分\n   {it['desc']}")
        lines.append("发送「兑换+编号」，例如：兑换6")
        return "\n".join(lines)

    def _redeem(self, item_id, user_id, username):
        data = self._load_user(user_id)
        if item_id not in self.SHOP:
            return "无效的商品编号，请检查后重试"
        item = self.SHOP[item_id]
        if data.get('points', 0) < item["price"]:
            return f"积分不足，当前：{data['points']}，所需：{item['price']}"
        data['points'] -= item["price"]
        if item_id in ("2", "4"):
            titles = list(self.dictionary.keys()) or ["无名"]
            data['status'] = random.choice(titles)
            self._save_user(user_id, data)
            return f"兑换成功！获得称号「{data['status']}」，剩余积分：{data['points']}"
        if item_id == "3":
            f = self.daily_fortune()
            self._save_user(user_id, data)
            return f"兑换成功！{f}\n剩余积分：{data['points']}"
        if item_id in ("5", "6"):
            bonus = random.randint(1000000, 50000000) if item_id == "5" else random.randint(1000, 500000)
            data['points'] += bonus
            self._save_user(user_id, data)
            return f"兑换成功！获得 {bonus} 积分，当前积分：{data['points']}"
        if item_id in ("7", "8", "9"):
            others = [fn[5:-5] for fn in os.listdir(SIGNIN_DIR)
                      if fn.startswith("user_") and fn.endswith(".json") and fn[5:-5] != str(user_id)]
            if others:
                target = random.choice(others)
                tdata = self._load_user(target)
                if item_id == "7":
                    cut = min(random.randint(1, 10000000), tdata.get('points', 0))
                    tdata['points'] = tdata.get('points', 0) - cut
                    self._save_user(target, tdata)
                    self._save_user(user_id, data)
                    return f"随机选择了{target}，减少{cut}分，剩余：{tdata['points']}，你的剩余：{data['points']}"
                if item_id == "8":
                    add = random.randint(1999, 1000000)
                    tdata['points'] = tdata.get('points', 0) + add
                    self._save_user(target, tdata)
                    self._save_user(user_id, data)
                    return f"随机选择了{target}，增加{add}分，剩余：{tdata['points']}，你的剩余：{data['points']}"
                if item_id == "9":
                    tdata['points'] = 0
                    self._save_user(target, tdata)
                    self._save_user(user_id, data)
                    return f"随机选择了{target}，积分已清零，你的剩余：{data['points']}"
            data['points'] += item["price"]
            self._save_user(user_id, data)
            return "兑换失败，暂无其他玩家，积分已退还"
        return None
