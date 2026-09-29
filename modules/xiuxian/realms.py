# -*- coding: utf-8 -*-
"""修仙境界：境界名称/阈值配置加载、子境界与飞升等级（数据层）"""

import json
import os

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
