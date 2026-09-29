# -*- coding: utf-8 -*-
"""修仙玩法指令入口（移植自 rqhbot rqhshen 插件）

把原插件的 filter_registry 指令注册改写成纯文本前缀解析：
- 不是修仙指令（含普通聊天）返回 None，交由调用方继续分发
- 需要回复时返回回复字符串
- 已处理但无文本回复时返回空串
"""

import asyncio
import json
import logging
import os
import re

from .storage import CultivationSystem

logger = logging.getLogger(__name__)

_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# 插件配置，enabled 可整体开关修仙功能
try:
    with open(os.path.join(_MODULE_DIR, "config.json"), "r", encoding="utf-8") as _f:
        PLUGIN_CONFIG = json.load(_f)
except (OSError, json.JSONDecodeError):
    PLUGIN_CONFIG = {}

# 系统实例惰性创建，避免 import 阶段就扫描全部玩家存档
_SYSTEM = None
# 同一用户串行执行，避免并发写档互相覆盖
_USER_LOCKS: dict = {}
_LOCK_LOCK = asyncio.Lock()

_HELP_TEXT = """📜 修仙帮助

开灵 | 打坐 | 突破 | 自动打坐(次数) | 修行(次数) | 修炼 | 修仙排行 | 修仙帮助

🎒 装备系统
- 背包：查看背包
- 装备 <物品名>：穿戴武器/护甲/法宝
- 卸下 <武器/护甲/法宝>：卸下装备
- 使用 <丹药名>：服用丹药增加修为
- 出售 <物品名>：出售换修为
- 丢弃 <物品名>：丢弃物品

打坐/突破/挑战有概率掉落装备，装备提升战力与修炼速度"""


def _get_system() -> CultivationSystem:
    """获取（并按需创建）修仙系统实例"""
    global _SYSTEM
    if _SYSTEM is None:
        _SYSTEM = CultivationSystem()
    return _SYSTEM


def _parse_times(arg: str, default: int = 50) -> int:
    """从参数中提取次数，支持「100」「100次」等写法，默认 50 次"""
    m = re.search(r"\d+", arg) if arg else None
    times = int(m.group()) if m else default
    return max(1, min(times, 1_000_000))


# ==================== 各指令实现（同步，返回回复文本） ====================

def _open_soul(system, user_id, username, arg):
    """开灵"""
    player = system.load_player(user_id, username)
    result = player.open_soul()
    system.save_player(player)
    return result


def _meditate(system, user_id, username, arg):
    """打坐"""
    player = system.load_player(user_id, username)
    result = player.meditate()
    system.save_player(player)
    return result


def _breakthrough(system, user_id, username, arg):
    """突破"""
    player = system.load_player(user_id, username)
    result = player.attempt_breakthrough()
    system.save_player(player)
    return result


def _auto_meditate(system, user_id, username, arg):
    """自动打坐 <次数>"""
    player = system.load_player(user_id, username)
    result = player.auto_meditate(_parse_times(arg))
    system.save_player(player)
    return result


def _cultivate(system, user_id, username, arg):
    """修行 <次数>：无惩罚自动打坐"""
    player = system.load_player(user_id, username)
    result = player.auto_meditate_no_penalty(_parse_times(arg))
    system.save_player(player)
    return result


def _status(system, user_id, username, arg):
    """修炼状态"""
    player = system.load_player(user_id, username)
    return (
        f"修炼状态\n"
        f"境界：{player.current_realm_name}\n"
        f"修为：{player.exp}/{player.next_threshold if player.next_threshold != float('inf') else 'MAX'}\n"
        f"突破：{player.total_breakthroughs} 次\n"
        f"总获得：{player.total_exp_gained}"
    )


def _ranking(system, user_id, username, arg):
    """修仙排行"""
    return system.get_ranking(10)


def _bag(system, user_id, username, arg):
    """背包"""
    return system.load_player(user_id, username).view_bag()


def _equip(system, user_id, username, arg):
    """装备 <物品名>"""
    if not arg:
        return "用法：装备 <武器/护甲/法宝名>\n例：装备 凡品灵剑"
    player = system.load_player(user_id, username)
    result = player.equip_item(arg)
    system.save_player(player)
    return result


def _unequip(system, user_id, username, arg):
    """卸下 <武器/护甲/法宝>"""
    if not arg:
        return "用法：卸下 <武器/护甲/法宝>"
    slot_map = {"武器": "weapon", "护甲": "armor", "法宝": "artifact", "artifact": "artifact"}
    player = system.load_player(user_id, username)
    result = player.unequip_item(slot_map.get(arg, arg))
    system.save_player(player)
    return result


def _use(system, user_id, username, arg):
    """使用 <丹药名>"""
    if not arg:
        return "用法：使用 <丹药名>\n例：使用 聚气丹"
    player = system.load_player(user_id, username)
    result = player.use_item(arg)
    system.save_player(player)
    return result


def _sell(system, user_id, username, arg):
    """出售 <物品名>"""
    if not arg:
        return "用法：出售 <物品名>\n例：出售 凡品灵剑"
    player = system.load_player(user_id, username)
    result = player.sell_item(arg)
    system.save_player(player)
    return result


def _discard(system, user_id, username, arg):
    """丢弃 <物品名>"""
    if not arg:
        return "用法：丢弃 <物品名>\n例：丢弃 凡品灵剑"
    player = system.load_player(user_id, username)
    result = player.discard_item(arg)
    system.save_player(player)
    return result


# 指令表：(前缀, 处理函数, 异常回复前缀)，长前缀放前面避免互相抢占
_COMMANDS = (
    ("修仙排行", _ranking, "查询"),
    ("自动打坐", _auto_meditate, "自动打坐"),
    ("开灵", _open_soul, "开灵"),
    ("打坐", _meditate, "打坐"),
    ("突破", _breakthrough, "突破"),
    ("修行", _cultivate, "修行"),
    ("修炼", _status, "查询"),
    ("背包", _bag, "查看背包"),
    ("卸下", _unequip, "卸下装备"),
    ("卸装", _unequip, "卸下装备"),
    ("装备", _equip, "穿戴装备"),
    ("使用", _use, "使用丹药"),
    ("出售", _sell, "出售"),
    ("丢弃", _discard, "丢弃"),
)


async def handle(text: str, group_id: str, user_id: str, username: str, reply_image=None) -> str | None:
    """修仙指令统一入口

    返回 None 表示不是修仙指令；返回字符串表示已处理（空串表示无需文本回复）。
    本玩法按用户维度存档，group_id 与 reply_image 暂不使用。
    """
    if not PLUGIN_CONFIG.get("enabled", True):
        return None
    t = (text or "").strip()
    if not t:
        return None
    # 精确指令
    if t == "修仙帮助":
        return _HELP_TEXT
    # 前缀指令（前后空格已在 strip 中放宽）
    for prefix, func, err in _COMMANDS:
        if t.startswith(prefix):
            arg = re.sub(rf"^{re.escape(prefix)}\s*", "", t).strip()
            async with _LOCK_LOCK:
                lock = _USER_LOCKS.setdefault(user_id, asyncio.Lock())
            async with lock:
                try:
                    return func(_get_system(), user_id, username, arg)
                except Exception as e:
                    logger.error(f"[xiuxian] {err}失败: {e}", exc_info=True)
                    return f"{err}失败: {e}"
    return None
