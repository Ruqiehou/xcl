# -*- coding: utf-8 -*-
"""工具命令：查词/粗查/天气/新闻/定位/转写/搜索"""

import re
import urllib.parse

from .utils import NumberToChinese, WeatherService, NewsService, IPQueryService


class ToolCommands:
    """工具命令处理器"""

    def __init__(self, dictionary: dict):
        self.dictionary = dictionary
        self.weather = WeatherService()
        self.news = NewsService()
        self.ip_svc = IPQueryService()
        self.num2cn = NumberToChinese()

    def lookup(self, word):
        """查词"""
        if not word:
            return "格式：查词 <单词>"
        if word in self.dictionary:
            return f"{word} ↔ {self.dictionary[word]}"
        # 反向：外文→中文
        rev = [w for w, d in self.dictionary.items() if d == word]
        if rev:
            return f"{word} ↔ {', '.join(rev)}"
        return f"抱歉，未找到「{word}」的双语信息。"

    def coarse_lookup(self, keyword):
        """粗查"""
        if not keyword:
            return "格式：粗查 <关键词>"
        hits = [w for w in self.dictionary.keys() if keyword in w]
        if not hits:
            return f"未找到包含「{keyword}」的单词"
        lines = "\n".join(f"{i+1}. {w}" for i, w in enumerate(hits))
        return f"找到 {len(hits)} 个包含「{keyword}」的单词：\n{lines}"

    async def weather_cmd(self, city):
        """天气查询"""
        if not city:
            return "格式：天气 <城市名>"
        r = self.weather.query_weather(city)
        if not r.get("success"):
            return f"天气查询失败：{r.get('error')}"
        data = r.get("data")
        if isinstance(data, dict):
            lines = [f"{city} 当前天气："]
            for k, v in list(data.items())[:12]:
                lines.append(f"{k}：{v}")
            return "\n".join(lines)
        return f"{city} 当前天气：\n{data}"

    async def news_cmd(self):
        """新闻查询"""
        data = self.news.get_news()
        if not data:
            return "获取新闻失败"
        if isinstance(data, dict):
            lines = ["📰 新闻速览："]
            for i, (k, v) in enumerate(list(data.items())[:10]):
                if isinstance(v, str):
                    lines.append(f"{i+1}. {v}")
                else:
                    lines.append(f"{i+1}. {k}：{v}")
            return "\n".join(lines)
        return f"新闻：\n{data}"

    def ip_cmd(self, ip):
        """IP 定位"""
        if not ip:
            return "格式：定位 <IP地址>"
        return f"定位 {ip}\n{self.ip_svc.query_ip(ip)}"

    def zhuanxie_cmd(self, num):
        """数字转中文"""
        num = num.strip()
        if not num:
            return "格式：转写 <数字>"
        try:
            return f"{num} 转写为 {self.num2cn.convert(num)}"
        except Exception as e:
            return f"转写失败：{e}"

    async def search_cmd(self, query):
        """百度搜索"""
        query = query.strip()
        if not query:
            return "格式：爬 <关键词>"
        search_url = f"https://www.baidu.com/s?wd={urllib.parse.quote(query)}"
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124',
                'Accept-Language': 'zh-CN,zh;q=0.9',
            }
            from bs4 import BeautifulSoup
            async with __import__('aiohttp').ClientSession() as session:
                async with session.get(search_url, headers=headers,
                                       timeout=__import__('aiohttp').ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return f"搜索失败，状态码：{resp.status}"
                    html = await resp.text(encoding='utf-8')
            soup = BeautifulSoup(html, 'html.parser')
            results = []
            for res in soup.find_all('div', class_='result')[:3]:
                title_el = res.find('h3') or res.find('a')
                if not title_el:
                    continue
                title = re.sub(r'\s+', ' ', title_el.get_text().strip())
                c_el = res.find('div', class_='c-abstract') or res.find('span', class_='c-font-normal')
                content = re.sub(r'\s+', ' ', c_el.get_text().strip())[:200] if c_el else "暂无摘要"
                results.append(f"• {title}\n  {content}")
            if results:
                return f"🔍 搜索「{query}」的结果：\n\n" + "\n\n".join(results) + f"\n\n完整搜索：{search_url}"
            return f"未找到「{query}」相关结果\n完整搜索：{search_url}"
        except Exception as e:
            return f"搜索失败：{e}\n您可直接访问：{search_url}"
