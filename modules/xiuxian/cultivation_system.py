# -*- coding: utf-8 -*-
"""修仙养成系统：境界、修为、突破、装备、背包、排行榜（移植自 rqhbot rqhshen 插件）"""

import random
import json
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# 模块所在目录：.../xcl/modules/xiuxian，境界配置随模块放置
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
# 项目根目录：.../xcl（bot.py 所在目录）
BASE_DIR = os.path.dirname(os.path.dirname(MODULE_DIR))
# 玩家数据目录：.../xcl/data/xiuxian，用户 ID 为 openid 字符串
DEFAULT_DATA_DIR = os.path.join(BASE_DIR, "data", "xiuxian")


def load_realms_from_json():
    """从JSON文件加载境界配置"""
    # 使用模块目录路径
    script_dir = MODULE_DIR
    json_path = os.path.join(script_dir, "jingjie.json")
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            realms = data.get('realms', [])
            thresholds = data.get('thresholds', [])
            
            # 如果JSON中没有预设的阈值，则按斐波那契数列生成
            if not thresholds and realms:
                thresholds = generate_fibonacci_thresholds(len(realms))
            
            return realms, thresholds
    else:
        # 默认配置 - 250个主要境界
        realms = [
            "练气期",
            "筑基期", 
            "金丹期",
            "元婴期",
            "化神期",
            "炼虚期",
            "合体期",
            "大乘期",
            "渡劫期",
            "散仙",
            "地仙",
            "天仙",
            "真仙",
            "玄仙",
            "金仙",
            "太乙金仙",
            "大至金仙", 
            "太乙玄仙",
            "大至玄仙",
            "太乙真仙",
            "大至真仙",
            "太乙天仙",
            "大至天仙",
            "大罗仙",
            "大罗金仙",
            "大罗散仙",
            "九天玄仙",
            "九天金仙",
            "九天真仙",
            "九天仙",
            "九天散仙",
            "太乙仙",
            "太乙圣",
            "大至圣",
            "太乙圣君",
            "大至圣君",
            "九天玄圣",
            "九天金圣",
            "九天真圣",
            "九天圣",
            "九天散圣",
            "准圣",
            "混元圣人",
            "太乙神将",
            "大至神将",
            "太一神将",
            "太乙天将",
            "大至天将",
            "太一天将",
            "太乙神相",
            "大至神相",
            "太一神相",
            "太乙天相",
            "大至天相",
            "太一天相",
            "太乙神君",
            "大至神君",
            "太一神君",
            "太乙天君",
            "大至天君",
            "太一天君",
            "太乙道君",
            "大至道君",
            "太一道君",
            "太乙帝君",
            "大至帝君",
            "太一帝君",
            "太乙神帝",
            "大至神帝",
            "太一神帝",
            "太乙天帝",
            "大至天帝",
            "太一天帝",
            "太乙神皇",
            "大至神皇",
            "太一神皇",
            "太乙天皇",
            "大至天皇",
            "太一天皇",
            "太乙神王",
            "大至神王",
            "太一神王",
            "太乙天王",
            "大至天王",
            "太一天王",
            "太乙星君",
            "大至星君",
            "太一星君",
            "太乙月君",
            "大至月君",
            "太一月君",
            "太乙日君",
            "大至日君",
            "太一日君",
            "太乙辰君",
            "大至辰君",
            "太一辰君",
            "太乙宿君",
            "大至宿君",
            "太一宿君",
            "天道",
            "大道",
            "混沌圣王",
            "鸿蒙至尊",
            "太初神主",
            "无极道祖",
            "太极仙尊",
            "阴阳法王",
            "五行真君",
            "八卦宗师",
            "九宫真人",
            "十方圣者",
            "百变仙师",
            "千幻神将",
            "万化道君",
            "虚无上人",
            "空灵仙长",
            "寂灭神僧",
            "涅槃佛祖",
            "轮回主宰",
            "造化仙翁",
            "乾坤道人",
            "天地法相",
            "宇宙圣贤",
            "星辰使者",
            "日月神君",
            "山河圣主",
            "江海仙宗",
            "风雷神将",
            "霜雪道君",
            "花鸟真人",
            "虫鱼仙长",
            "草木神翁",
            "金石法王",
            "云雾宗师",
            "烟霞真人",
            "霞光圣者",
            "紫气仙长",
            "青龙神将",
            "白虎神君",
            "朱雀仙师",
            "玄武道长",
            "麒麟圣兽",
            "凤凰神禽",
            "鲲鹏仙羽",
            "蛟龙神鳞",
            "貔貅财神",
            "饕餮食神",
            "睚眦兵神",
            "嘲风建筑神",
            "蒲牢钟神",
            "狻猊火神",
            "狴犴狱神",
            "负屃文神",
            "螭吻水神",
            "腾蛇游神",
            "勾陈天神",
            "螣蛇地神",
            "玄武水神",
            "朱雀火神",
            "白虎金神",
            "青龙木神",
            "黄龙土神",
            "苍龙东神",
            "赤龙南神",
            "白龙西神",
            "墨龙北神",
            "金龙财神",
            "银龙宝神",
            "铜龙运神",
            "铁龙力神",
            "玉龙祥神",
            "珠龙瑞神",
            "翠龙福神",
            "玛瑙龙吉神",
            "琥珀龙顺神",
            "珊瑚龙安神",
            "琉璃龙泰神",
            "水晶龙和神",
            "钻石龙昌神",
            "珍珠龙盛神",
            "翡翠龙兴神",
            "黄金龙隆神",
            "白银龙丰神",
            "青铜龙盛神",
            "钢铁龙强神",
            "玉石龙祥神",
            "玛瑙龙庆神",
            "翡翠龙嘉神",
            "珍珠龙福神",
            "钻石龙贵神",
            "水晶龙宝神",
            "琥珀龙瑞神",
            "珊瑚龙吉神",
            "琉璃龙祥神",
            "云母龙安神",
            "水晶龙泰神",
            "冰晶龙和神",
            "雪花龙清神",
            "雨滴龙润神",
            "露珠龙泽神",
            "甘露龙恩神",
            "朝霞龙辉神",
            "夕阳龙照神",
            "明月龙华神",
            "繁星龙耀神",
            "银河龙瀚神",
            "彩云龙霓神",
            "飞虹龙桥神",
            "雷电龙威神",
            "闪电龙迅神",
            "暴雨龙沛神",
            "微风龙和神",
            "清风龙爽神",
            "暖风龙温神",
            "寒风龙冽神",
            "春风龙生神",
            "夏风龙长神",
            "秋风龙收神",
            "冬风龙藏神",
            "四季龙轮神",
            "昼夜龙恒神",
            "晨昏龙序神",
            "黎明龙启神",
            "正午龙烈神",
            "黄昏龙暮神",
            "深夜龙静神",
            "子时龙初神",
            "丑时龙萌神",
            "寅时龙生神",
            "卯时龙明神",
            "辰时龙升神",
            "巳时龙进神",
            "午时龙旺神",
            "未时龙缓神",
            "申时龙收神",
            "酉时龙成神",
            "戌时龙固神",
            "亥时龙藏神",
            "天干甲龙",
            "天干乙龙",
            "天干丙龙",
            "天干丁龙",
            "天干戊龙",
            "天干己龙",
            "天干庚龙",
            "天干辛龙",
            "天干壬龙",
            "天干癸龙",
            "地支子龙",
            "地支丑龙",
            "地支寅龙",
            "地支卯龙",
            "地支辰龙",
            "地支巳龙",
            "地支午龙",
            "地支未龙",
            "地支申龙",
            "地支酉龙",
            "地支戌龙",
            "地支亥龙",
            "三才天地人龙",
            "四象青龙",
            "五方中央龙",
            "六合八荒龙",
            "七星北斗龙",
            "八封乾坤龙",
            "九州华夏龙",
            "十方世界龙",
            "十二生肖龙",
            "二十四节气龙",
            "三十六计谋龙",
            "七十二变化龙",
            "八十一难渡龙",
            "九九归元龙",
            "百炼成钢龙",
            "千锤百炼龙",
            "万法归宗龙",
            "无上至尊龙"
        ]
        
        # 根据斐波那契数列生成突破所需经验列表
        thresholds = []
        for i in range(len(realms)):
            if i == 0:
                thresholds.append(100)      # 练气 -> 筑基 需要 100
            elif i == 1:
                thresholds.append(200)      # 筑基 -> 金丹 需要 200
            else:
                # 斐波那契逻辑：当前 = 前一个 + 前两个
                val = thresholds[i-1] + thresholds[i-2]
                thresholds.append(val)
        
        return realms, thresholds

def generate_fibonacci_thresholds(num_realms):
    """根据斐波那契数列生成突破所需经验列表"""
    thresholds = []
    for i in range(num_realms):
        if i == 0:
            thresholds.append(100)      # 第一个境界需要100经验
        elif i == 1:
            thresholds.append(200)      # 第二个境界需要200经验
        else:
            # 斐波那契逻辑：当前 = 前一个 + 前两个
            val = thresholds[i-1] + thresholds[i-2]
            thresholds.append(val)
    
    return thresholds

# 1. 从配置文件加载境界名称列表
REALM_NAMES, REALM_THRESHOLDS = load_realms_from_json()

# 为每个境界添加子层级 (0-8，共9个子层)
def generate_sub_realms():
    sub_realms = []
    for idx, realm_name in enumerate(REALM_NAMES):
        for i in range(9):  # 0-8 共9个子层
            sub_realms.append(f"{idx+1}.{realm_name}·{i+1}")
    # 最终境界不划分子层
    sub_realms.append(f"{len(REALM_NAMES)}.{REALM_NAMES[-1]}")  # 最后一个境界保持原样
    return sub_realms

SUB_REALMS = generate_sub_realms()

# 为每个子境界设置突破经验
def generate_sub_thresholds():
    sub_thresholds = []
    for i, base_threshold in enumerate(REALM_THRESHOLDS):
        # 每个主境界分为9个子层，每个子层需要 1/9 的基础突破经验
        if base_threshold == float('inf'):  # 最后一个境界
            sub_step = float('inf')
        else:
            sub_step = base_threshold // 9
        for j in range(9):
            sub_thresholds.append(sub_step)
    # 最后一个境界不需要突破
    sub_thresholds.append(float('inf'))
    return sub_thresholds

SUB_REALM_THRESHOLDS = generate_sub_thresholds()

# 飞升境界等级列表
ASCENSION_LEVELS = [9, 49, 159, 199, 279]

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

class CultivationSystem:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = DEFAULT_DATA_DIR
        self.data_dir = data_dir
        self.players = {}
        self._ensure_data_dir_exists()
        self.load_all_players()
    
    def _ensure_data_dir_exists(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _player_file(self, player_id: str) -> str:
        """玩家存档路径：player_<openid>.json"""
        return os.path.join(self.data_dir, f"player_{player_id}.json")
    
    def load_player(self, player_id: str, username: str):
        """加载或创建玩家数据（player_id 为 openid 字符串）"""
        player_file = self._player_file(player_id)
        
        if os.path.exists(player_file):
            with open(player_file, 'r', encoding='utf-8') as f:
                player_data = json.load(f)
                player = Cultivator(
                    username=username,  # 总是使用最新用户名
                    player_id=player_id,
                    realm_index=player_data.get('realm_index', 0),
                    exp=player_data.get('exp', 0),
                    last_meditate=player_data.get('last_meditate', ''),
                    total_exp_gained=player_data.get('total_exp_gained', 0),
                    total_breakthroughs=player_data.get('total_breakthroughs', 0),
                    items=player_data.get('items', []),
                    is_soul_opened=player_data.get('is_soul_opened', False),
                    is_ascended=player_data.get('is_ascended', False),
                    ascension_count=player_data.get('ascension_count', 0),
                    equipped=player_data.get('equipped', {})
                )
        else:
            player = Cultivator(username, player_id)
        
        self.players[player_id] = player
        return player
    
    def save_player(self, player):
        """保存玩家数据"""
        player_file = self._player_file(player.player_id)
        player_data = {
            'username': player.username,
            'player_id': player.player_id,
            'realm_index': player.realm_index,
            'exp': player.exp,
            'last_meditate': player.last_meditate,
            'total_exp_gained': player.total_exp_gained,
            'total_breakthroughs': player.total_breakthroughs,
            'items': player.items,
            'is_soul_opened': player.is_soul_opened,
            'is_ascended': player.is_ascended,
            'ascension_count': player.ascension_count,
            'equipped': player.equipped
        }
        
        with open(player_file, 'w', encoding='utf-8') as f:
            json.dump(player_data, f, ensure_ascii=False, indent=2)
    
    def load_all_players(self):
        """加载所有玩家数据到内存缓存"""
        if not os.path.exists(self.data_dir):
            return
        
        for filename in os.listdir(self.data_dir):
            if filename.startswith("player_") and filename.endswith(".json"):
                player_id = filename[len("player_"):-len(".json")]
                try:
                    self.load_player(player_id, f"User_{player_id}")
                except Exception as e:
                    logger.error(f"加载玩家文件 {filename} 时出错: {e}")
                    continue
    
    def load_all_players_from_files(self):
        """从文件加载所有玩家数据，不使用缓存 - 用于排行榜等需要最新数据的场景"""
        players = []
        if not os.path.exists(self.data_dir):
            return players
        
        for filename in os.listdir(self.data_dir):
            if filename.startswith("player_") and filename.endswith(".json"):
                player_id = filename[len("player_"):-len(".json")]
                player_file = os.path.join(self.data_dir, filename)
                try:
                    with open(player_file, 'r', encoding='utf-8') as f:
                        player_data = json.load(f)
                        player = Cultivator(
                            username=player_data.get('username', f'User_{player_id}'),
                            player_id=player_id,
                            realm_index=player_data.get('realm_index', 0),
                            exp=player_data.get('exp', 0),
                            last_meditate=player_data.get('last_meditate', ''),
                            total_exp_gained=player_data.get('total_exp_gained', 0),
                            total_breakthroughs=player_data.get('total_breakthroughs', 0),
                            items=player_data.get('items', []),
                            is_soul_opened=player_data.get('is_soul_opened', False),
                            is_ascended=player_data.get('is_ascended', False),
                            ascension_count=player_data.get('ascension_count', 0),
                            equipped=player_data.get('equipped', {})
                        )
                        players.append(player)
                except Exception as e:
                    logger.error(f"加载玩家文件 {filename} 时出错: {e}")
                    continue
        
        return players
    
    def get_ranking(self, top_n=10):
        """获取排行榜"""
        players = self.load_all_players_from_files()
        
        if not players:
            return "暂无玩家数据"
        
        sorted_players = sorted(players, key=lambda p: p.realm_index, reverse=True)
        
        ranking_info = "🏆 修仙排行榜\n\n"
        for i, player in enumerate(sorted_players[:top_n], 1):
            ranking_info += f"{i}. {player.username} - {player.current_realm_name}\n"
        
        return ranking_info


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
