# -*- coding: utf-8 -*-
"""修仙装备系统：品阶/类型常量、装备生成与物品比较（数据层）"""

import random

# ==================== 装备系统 ====================
EQUIPMENT_GRADES = ["凡品", "黄品", "玄品", "地品", "天品", "仙品", "神品", "混沌"]
GRADE_MULTIPLIER = [1, 2, 4, 8, 16, 32, 64, 128]
EQUIPMENT_TYPES = {
    "weapon": "武器",
    "armor": "护甲",
    "artifact": "法宝",
    "pill": "丹药",
}
EQUIPMENT_TEMPLATES = {
    "weapon": ["灵剑", "飞剑", "战斧", "长枪", "神弓", "法杖"],
    "armor": ["道袍", "仙衣", "战甲", "灵铠", "护盾"],
    "artifact": ["玉佩", "宝珠", "葫芦", "灵灯", "金钟"],
    "pill": ["聚气丹", "培元丹", "破境丹", "洗髓丹", "悟道丹"],
}
EQUIPMENT_DESC = {
    "weapon": "攻击",
    "armor": "防御",
    "artifact": "修炼",
    "pill": "服用后增加修为",
}
# 可穿戴的装备类型（丹药不入装）
WEARABLE_TYPES = ["weapon", "armor", "artifact"]


def generate_equipment(realm_index: int) -> dict:
    """根据境界随机生成一件装备/丹药，境界越高越可能出高品阶"""
    equip_type = random.choice(list(EQUIPMENT_TEMPLATES.keys()))
    name = random.choice(EQUIPMENT_TEMPLATES[equip_type])

    # 品阶随境界提升：基础品阶 = 境界/40，再叠加随机浮动
    max_grade = min(len(EQUIPMENT_GRADES) - 1, realm_index // 40)
    base = max(0, max_grade // 2)
    grade_idx = max(0, min(len(EQUIPMENT_GRADES) - 1, base + random.randint(0, max(0, max_grade - base)) + random.randint(0, 1)))
    grade = EQUIPMENT_GRADES[grade_idx]
    multiplier = GRADE_MULTIPLIER[grade_idx]

    if equip_type == "pill":
        bonus = (50 + realm_index * 3) * multiplier
    elif equip_type == "weapon":
        bonus = (10 + realm_index // 2) * multiplier
    elif equip_type == "armor":
        bonus = (8 + realm_index // 2) * multiplier
    else:  # artifact
        bonus = (5 + realm_index // 4) * multiplier

    return {
        "name": f"{grade}{name}",
        "type": equip_type,
        "grade": grade,
        "bonus": int(bonus),
        "count": 1,
    }


def items_equal(a: dict, b: dict) -> bool:
    """判断两件物品是否同名同阶（用于背包堆叠）"""
    return a.get("name") == b.get("name")
