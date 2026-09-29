# -*- coding: utf-8 -*-
"""CultivationSystem：玩家存档读写与排行榜（持久化层）"""

import json
import os
import logging

from .cultivator import Cultivator
from .realms import DEFAULT_DATA_DIR

logger = logging.getLogger(__name__)


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
