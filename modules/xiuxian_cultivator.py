# -*- coding: utf-8 -*-
"""修仙者 Cultivator：打坐、突破、飞升、战斗、装备与背包（领域对象）"""

import random
from typing import Optional

from .xiuxian_realms import (ASCENSION_LEVELS, REALM_NAMES, SUB_REALMS,
                             SUB_REALM_THRESHOLDS)
from .xiuxian_equipment import (EQUIPMENT_TYPES, WEARABLE_TYPES,
                                generate_equipment, items_equal)


class Cultivator:
    def __init__(self, username: str, player_id: str, realm_index: int = 0, exp: int = 0, 
                 last_meditate: str = '', total_exp_gained: int = 0, 
                 total_breakthroughs: int = 0, items: list = None, is_soul_opened: bool = False,
                 is_ascended: bool = False, ascension_count: int = 0, equipped: dict = None):
        self.username = username
        self.player_id = player_id
        self.realm_index = realm_index
        self.exp = exp
        self.last_meditate = last_meditate
        self.total_exp_gained = total_exp_gained
        self.total_breakthroughs = total_breakthroughs
        self.items = items if items is not None else []
        self.is_soul_opened = is_soul_opened
        self.is_ascended = is_ascended
        self.ascension_count = ascension_count
        # 已穿戴装备 {weapon/armor/artifact: item_dict 或 None}
        self.equipped = equipped if equipped is not None else {"weapon": None, "armor": None, "artifact": None}

    @property
    def current_realm_name(self):
        """获取当前境界名称（包括子境界）"""
        if self.realm_index >= len(SUB_REALMS):
            return f"{SUB_REALMS[-1]} (大圆满)"
        return SUB_REALMS[self.realm_index]

    @property
    def next_threshold(self):
        """获取突破到下一境界所需的经验值"""
        if self.realm_index >= len(SUB_REALM_THRESHOLDS):
            return float('inf')
        return SUB_REALM_THRESHOLDS[self.realm_index]


    def open_soul(self):
        """开灵功能 - 踏入仙途"""
        if self.is_soul_opened:
            return "已开灵，无需重复"
        
        success_rate = random.randint(1, 100)
        if success_rate <= 80:
            self.is_soul_opened = True
            self.realm_index = 0
            self.exp = 0
            return f"开灵成功！踏入【{REALM_NAMES[0]}】修士"
        else:
            return "开灵失败，请重试"

    def meditate(self):
        """打坐功能"""
        if not self.is_soul_opened:
            return "未开灵，请先开灵"
        
        current_exp = self.exp
        min_gain = max(10, int(10 + current_exp ** 0.5 * 2))
        max_gain = max(30, int(30 + current_exp ** 0.7 * 5))
        
        gain = random.randint(min_gain, max_gain)
        # 法宝修炼加成（百分比）
        if self.cultivation_bonus > 0:
            gain = int(gain * (1 + self.cultivation_bonus / 100))
        self.exp += gain
        self.total_exp_gained += gain
        
        msg = f"打坐成功，修为 +{gain}"
        
        breakthrough_occurred = False
        while self.realm_index < len(SUB_REALMS) - 1 and self.exp >= self.next_threshold:
            realm_stage = (self.realm_index // 9) + 1
            success_rate = max(0.6, 0.85 - (realm_stage * 0.005))
            
            if random.random() > success_rate:
                loss_amount = self.exp // 2
                self.exp = max(0, self.exp - loss_amount)
                msg += f"\n突破失败，修为减半 -{loss_amount}"
                break
            else:
                self.realm_index += 1
                self.total_breakthroughs += 1
                breakthrough_occurred = True
                current_realm = SUB_REALMS[self.realm_index]
                msg += f"\n自动突破至：【{current_realm}】"
        
        msg += f"\n修为：{self.exp} / {self.next_threshold if self.next_threshold != float('inf') else 'MAX'}"

        if breakthrough_occurred:
            if self.realm_index < len(SUB_REALMS) - 1:
                msg += f"\n下一目标：{SUB_REALMS[self.realm_index + 1]}"
            else:
                msg += "\n已达最高境界"
        elif self.realm_index >= len(SUB_REALMS) - 1:
            msg += "\n已达最高境界"
        else:
            msg += f"\n还需 {self.next_threshold - self.exp} 修为突破"

        drop = self.roll_drop()
        if drop:
            self.add_item(drop)
            msg += f"\n\n🎁 获得【{drop['name']}】！"

        return msg

    def attempt_breakthrough(self):
        """手动突破功能"""
        if not self.is_soul_opened:
            return "未开灵，请先开灵"
        
        if self.realm_index >= len(SUB_REALMS) - 1:
            return "已达最高境界"
        
        if self.exp < self.next_threshold:
            return f"修为不足，需要 {self.next_threshold}，当前 {self.exp}"
        
        realm_stage = (self.realm_index // 9) + 1
        success_rate = max(0.6, 0.85 - (realm_stage * 0.005))
        
        if random.random() > success_rate:
            loss_percentage = random.uniform(0.05, 0.15)
            loss_amount = int(self.exp * loss_percentage)
            self.exp = max(0, self.exp - loss_amount)
            return f"突破失败，损失 {loss_amount} 修为\n当前：{self.exp}/{self.next_threshold if self.next_threshold != float('inf') else 'MAX'}"
        
        breakthrough_count = 0
        while self.realm_index < len(SUB_REALMS) - 1 and self.exp >= self.next_threshold:
            realm_stage = (self.realm_index // 9) + 1
            success_rate = max(0.6, 0.85 - (realm_stage * 0.005))
            
            if random.random() > success_rate:
                loss_percentage = random.uniform(0.05, 0.15)
                loss_amount = int(self.exp * loss_percentage)
                self.exp = max(0, self.exp - loss_amount)
                return f"突破失败，损失 {loss_amount} 修为\n当前：{self.exp}/{self.next_threshold if self.next_threshold != float('inf') else 'MAX'}"
            
            self.realm_index += 1
            self.total_breakthroughs += 1
            breakthrough_count += 1
        
        if breakthrough_count > 0:
            msg = f"突破成功！晋升至：{self.current_realm_name}\n累计突破：{self.total_breakthroughs} 次"
            drop = self.roll_drop()
            if drop:
                self.add_item(drop)
                msg += f"\n\n🎁 获得【{drop['name']}】！"
            return msg
        else:
            return f"修为不足，需要 {self.next_threshold}"

    def attempt_ascension(self):
        """飞升功能 - 在9、49、159、199、279级对应的大境界可以飞升"""
        if not self.is_soul_opened:
            return "未开灵，请先开灵"
        
        # 计算当前主境界（从1开始）
        current_main_realm = (self.realm_index // 9) + 1
        
        # 检查当前是否在可以飞升的主境界
        if current_main_realm not in ASCENSION_LEVELS:
            return f"当前 {current_main_realm}级 无法飞升\n可飞升：{', '.join(map(str, ASCENSION_LEVELS))}级"
        
        # 飞升成功率30%
        if random.randint(1, 100) <= 30:
            # 飞升成功
            self.is_ascended = True
            self.ascension_count += 1
            
            msg = f"飞升成功！第 {self.ascension_count} 次\n"
            msg += f"境界：【{self.current_realm_name}】\n"
            msg += f"修为：{self.exp}"
            if current_main_realm == 279:
                msg += "\n279级飞升后无法再突破"
        else:
            # 飞升失败，扣除一半经验
            loss_amount = self.exp // 2
            self.exp = max(0, self.exp - loss_amount)
            msg = f"飞升失败，损失一半修为 -{loss_amount}\n"
            msg += f"当前修为：{self.exp} / {self.next_threshold if self.next_threshold != float('inf') else 'MAX'}"
        
        return msg

    def auto_meditate(self, times: int = 50):
        """自动打坐功能，默认50次，最高1000次"""
        if not self.is_soul_opened:
            return "未开灵，请先开灵"
        
        times = max(1, min(times, 1_000_000))
        
        total_gain = 0
        breakthrough_count = 0
        messages = []
        
        for i in range(times):
            current_exp = self.exp
            min_gain = max(10, int(10 + current_exp ** 0.5 * 2))
            max_gain = max(30, int(30 + current_exp ** 0.7 * 5))
            
            gain = random.randint(min_gain, max_gain)
            if self.cultivation_bonus > 0:
                gain = int(gain * (1 + self.cultivation_bonus / 100))
            self.exp += gain
            self.total_exp_gained += gain
            total_gain += gain
            
            # 检查是否突破
            while self.realm_index < len(SUB_REALMS) - 1 and self.exp >= self.next_threshold:
                realm_stage = (self.realm_index // 9) + 1
                success_rate = max(0.6, 0.85 - (realm_stage * 0.005))
                
                if random.random() > success_rate:
                    loss_amount = self.exp // 2
                    self.exp = max(0, self.exp - loss_amount)
                    messages.append(f"突破失败，修为减半 -{loss_amount}")
                    break
                else:
                    self.realm_index += 1
                    self.total_breakthroughs += 1
                    breakthrough_count += 1
                    current_realm = SUB_REALMS[self.realm_index]
                    messages.append(f"突破至：【{current_realm}】")
        
        # 有突破时掉落装备
        if breakthrough_count > 0:
            drop = self.roll_drop()
            if drop:
                self.add_item(drop)
                result_msg_note = f"\n\n🎁 获得【{drop['name']}】！"
            else:
                result_msg_note = ""
        else:
            result_msg_note = ""
        
        # 构建最终结果消息
        result_msg = f"自动打坐 {times} 次完成！\n"
        result_msg += f"总获得修为：+{total_gain}\n"
        result_msg += f"累计突破：{breakthrough_count} 次\n"
        result_msg += f"最终境界：{self.current_realm_name}\n"
        result_msg += f"最终修为：{self.exp} / {self.next_threshold if self.next_threshold != float('inf') else 'MAX'}"
        
        if messages:
            result_msg += "\n\n详细过程：\n" + "\n".join(messages[-10:])  # 只显示最后10条消息避免过长
        result_msg += result_msg_note
        
        return result_msg

    def auto_meditate_no_penalty(self, times: int = 50):
        """无惩罚自动打坐，默认50次，最高100万次"""
        if not self.is_soul_opened:
            return "未开灵，请先开灵"
        
        times = max(1, min(times, 1_000_000))
        
        total_gain = 0
        breakthrough_count = 0
        messages = []
        
        for i in range(times):
            current_exp = self.exp
            min_gain = max(10, int(10 + current_exp ** 0.5 * 2))
            max_gain = max(30, int(30 + current_exp ** 0.7 * 5))
            
            gain = random.randint(min_gain, max_gain)
            if self.cultivation_bonus > 0:
                gain = int(gain * (1 + self.cultivation_bonus / 100))
            self.exp += gain
            self.total_exp_gained += gain
            total_gain += gain
            
            # 只突破，失败不扣修为
            while self.realm_index < len(SUB_REALMS) - 1 and self.exp >= self.next_threshold:
                self.realm_index += 1
                self.total_breakthroughs += 1
                breakthrough_count += 1
                messages.append(f"突破至：【{SUB_REALMS[self.realm_index]}】")
        
        if breakthrough_count > 0:
            drop = self.roll_drop()
            result_msg_note = f"\n\n🎁 获得【{drop['name']}】！" if drop else ""
        else:
            result_msg_note = ""
        
        result_msg = f"修行 {times} 次完成！\n"
        result_msg += f"总获得修为：+{total_gain}\n"
        result_msg += f"累计突破：{breakthrough_count} 次\n"
        result_msg += f"最终境界：{self.current_realm_name}\n"
        result_msg += f"最终修为：{self.exp} / {self.next_threshold if self.next_threshold != float('inf') else 'MAX'}"
        
        if messages:
            result_msg += "\n\n详细过程：\n" + "\n".join(messages[-10:])
        result_msg += result_msg_note
        
        return result_msg

    def attack(self, opponent):
        """攻击其他玩家（武器加攻击，护甲减免伤害）"""
        self_power = self.realm_index * 100 + self.exp + self.attack_bonus
        opponent_power = opponent.realm_index * 100 + opponent.exp + opponent.attack_bonus
        
        total_power = self_power + opponent_power
        if total_power == 0:
            win_prob = 0.5
        else:
            win_prob = self_power / total_power
        
        win_prob = win_prob * 0.7 + random.random() * 0.3
        
        if random.random() < win_prob:
            opponent_loss = max(0, opponent.exp // 2 - self.defense_bonus)
            opponent.exp = max(0, opponent.exp - opponent_loss)
            
            self_loss = max(0, self.exp // 3 - self.defense_bonus)
            self.exp = max(0, self.exp - self_loss)
            
            self.check_and_update_realm_after_attack()
            opponent.check_and_update_realm_after_attack()
            
            msg = f"重创 {opponent.username}，对方 -{opponent_loss}，自身 -{self_loss}\n对方剩余：{opponent.exp}，自身剩余：{self.exp}"
            drop = self.roll_drop()
            if drop:
                self.add_item(drop)
                msg += f"\n\n🎁 获得【{drop['name']}】！"
            return msg
        else:
            opponent_loss = max(0, opponent.exp // 3 - self.defense_bonus)
            opponent.exp = max(0, opponent.exp - opponent_loss)
            
            self_loss = max(0, self.exp // 2 - self.defense_bonus)
            self.exp = max(0, self.exp - self_loss)
            
            self.check_and_update_realm_after_attack()
            opponent.check_and_update_realm_after_attack()
            
            msg = f"攻击被 {opponent.username} 抵御，对方 -{opponent_loss}，自身 -{self_loss}\n对方剩余：{opponent.exp}，自身剩余：{self.exp}"
            drop = self.roll_drop()
            if drop:
                self.add_item(drop)
                msg += f"\n\n🎁 获得【{drop['name']}】！"
            return msg

    def check_and_update_realm_after_attack(self):
        """在攻击后检查是否需要降级：修为归零时（当前境界修为耗尽）降一级"""
        if self.exp == 0 and self.realm_index > 0:
            self.realm_index -= 1

    # ==================== 装备/背包 ====================

    @staticmethod
    def _format_item(item: dict) -> str:
        """格式化单件物品为文本"""
        equip_type = EQUIPMENT_TYPES.get(item.get("type", ""), "物品")
        return f"{item['name']}（{item['grade']}{equip_type} +{item['bonus']}）x{item.get('count', 1)}"

    def _find_item(self, name: str) -> Optional[dict]:
        """按名称查找背包中的物品"""
        for item in self.items:
            if item.get("name") == name or name in item.get("name", ""):
                return item
        return None

    def add_item(self, item: dict) -> None:
        """将物品加入背包，同名同阶自动堆叠"""
        for existing in self.items:
            if items_equal(existing, item):
                existing["count"] = existing.get("count", 1) + item.get("count", 1)
                return
        self.items.append(item)

    def _equipped_bonus(self, equip_type: str) -> int:
        """获取某类已穿戴装备的加成值"""
        item = self.equipped.get(equip_type)
        if item:
            return item.get("bonus", 0)
        return 0

    @property
    def attack_bonus(self) -> int:
        """武器提供的攻击加成"""
        return self._equipped_bonus("weapon")

    @property
    def defense_bonus(self) -> int:
        """护甲提供的防御加成"""
        return self._equipped_bonus("armor")

    @property
    def cultivation_bonus(self) -> int:
        """法宝提供的修炼加成（百分比）"""
        return self._equipped_bonus("artifact")

    def view_bag(self) -> str:
        """查看背包"""
        if not self.items:
            return f"{self.username} 的背包空空如也，快去打坐/突破获取装备吧！"
        lines = [f"🎒 {self.username} 的背包："]
        for i, item in enumerate(self.items, 1):
            tag = ""
            if item.get("type") in WEARABLE_TYPES and self.equipped.get(item.get("type")) and \
                    self.equipped[item.get("type")].get("name") == item["name"]:
                tag = " [已穿戴]"
            lines.append(f"{i}. {self._format_item(item)}{tag}")
        # 显示已穿戴装备
        equipped_part = []
        for slot in WEARABLE_TYPES:
            item = self.equipped.get(slot)
            if item:
                equipped_part.append(f"{EQUIPMENT_TYPES[slot]}：{item['name']}(+{item['bonus']})")
        if equipped_part:
            lines.append("")
            lines.append("⚔️ 已穿戴：" + " | ".join(equipped_part))
        return "\n".join(lines)

    def equip_item(self, name: str) -> str:
        """穿戴装备（武器/护甲/法宝），同类自动替换旧装备"""
        item = self._find_item(name)
        if not item:
            return f"背包中没有【{name}】"
        if item.get("type") not in WEARABLE_TYPES:
            return f"【{item['name']}】是{EQUIPMENT_TYPES.get(item['type'], '物品')}，无法穿戴，请使用"
        slot = item["type"]
        old = self.equipped.get(slot)
        self.equipped[slot] = item
        item["count"] -= 1
        if item["count"] <= 0:
            self.items.remove(item)
        msg = f"已穿戴【{item['name']}】(+{item['bonus']})"
        if old:
            # 旧装备放回背包
            self.add_item(old)
            msg += f"\n卸下旧装备【{old['name']}】已放回背包"
        return msg

    def unequip_item(self, slot_type: str) -> str:
        """卸下指定类型装备"""
        if slot_type not in WEARABLE_TYPES:
            return "请指定卸下类型：武器 / 护甲 / 法宝"
        item = self.equipped.get(slot_type)
        if not item:
            return f"未穿戴{EQUIPMENT_TYPES[slot_type]}"
        self.add_item(item)
        self.equipped[slot_type] = None
        return f"已卸下【{item['name']}】，放回背包"

    def use_item(self, name: str) -> str:
        """使用丹药"""
        item = self._find_item(name)
        if not item:
            return f"背包中没有【{name}】"
        if item.get("type") != "pill":
            return f"【{item['name']}】是{EQUIPMENT_TYPES.get(item['type'], '物品')}，无法服用"
        gain = item["bonus"]
        self.exp += gain
        self.total_exp_gained += gain
        item["count"] -= 1
        if item["count"] <= 0:
            self.items.remove(item)
        msg = f"服用【{item['name']}】，修为 +{gain}"
        # 服用后可能自动突破
        while self.realm_index < len(SUB_REALMS) - 1 and self.exp >= self.next_threshold:
            self.realm_index += 1
            self.total_breakthroughs += 1
            msg += f"\n境界提升至：【{self.current_realm_name}】"
        return msg

    def sell_item(self, name: str) -> str:
        """出售装备/丹药换取修为"""
        item = self._find_item(name)
        if not item:
            return f"背包中没有【{name}】"
        # 已穿戴的不可出售
        for slot, equipped in self.equipped.items():
            if equipped and equipped.get("name") == item["name"]:
                return f"【{item['name']}】已穿戴，请先卸下"
        gain = item["bonus"]
        self.exp += gain
        self.total_exp_gained += gain
        item["count"] -= 1
        if item["count"] <= 0:
            self.items.remove(item)
        return f"出售【{item['name']}】，获得修为 +{gain}"

    def discard_item(self, name: str) -> str:
        """丢弃物品"""
        item = self._find_item(name)
        if not item:
            return f"背包中没有【{name}】"
        for slot, equipped in self.equipped.items():
            if equipped and equipped.get("name") == item["name"]:
                return f"【{item['name']}】已穿戴，请先卸下"
        self.items.remove(item)
        return f"已丢弃【{item['name']}】"

    def roll_drop(self) -> Optional[dict]:
        """判定并生成掉落装备，无掉落返回 None"""
        if random.random() > 0.05:  # 5% 掉率
            return None
        return generate_equipment(self.realm_index)
