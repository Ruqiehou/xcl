# -*- coding: utf-8 -*-
"""工具类：数字转中文、天气/新闻/IP 查询服务"""

import json
import os
import re
import urllib.parse
import urllib.request

import requests


class NumberToChinese:
    """数字转中文读法"""

    def __init__(self):
        self.digits = '零一二三四五六七八九'
        self.units = ['', '十', '百', '千']
        self.big_units = ['', '万', '亿', '兆', '京', '垓', '秭', '穰', '沟', '涧', '正', '载']

    def convert(self, num):
        s = str(num).strip() if isinstance(num, str) else str(num)
        if not s:
            raise ValueError("输入不能为空")
        if 'e' in s.lower():
            s = f"{float(s):.15f}".rstrip('0').rstrip('.')
        if '.' in s:
            return self._float(s)
        if '-' in s:
            raise ValueError("无效的数字格式")
        return self._integer(s)

    def _float(self, s):
        ipart, dpart = s.split('.', 1)
        int_cn = self._integer(ipart or "0")
        dec_cn = ''.join(self.digits[int(d)] for d in dpart if d.isdigit())
        return f"{int_cn}点{dec_cn}"

    def _integer(self, s):
        s = s.lstrip('0')
        if not s:
            return "零"
        if len(s) > 36:
            raise ValueError(f"数字过长，最大支持36位数，当前为{len(s)}位")
        result, group = "", 0
        for i in range(len(s), 0, -4):
            start = max(0, i - 4)
            section = int(s[start:i]) if s[start:i] else 0
            if section != 0:
                chunk = self._section(section)
                if group > 0:
                    chunk += self.big_units[group]
                result = chunk + result
            elif group > 0 and result and not result.startswith("零"):
                result = "零" + result
            group += 1
        if result.startswith("一十"):
            result = result[1:]
        return result

    def _section(self, n):
        if n == 0:
            return "零"
        result, s, ln = "", str(n), len(str(n))
        for i, ch in enumerate(s):
            d = int(ch)
            unit = self.units[ln - i - 1]
            if d != 0:
                result += self.digits[d] + unit
            elif result and result[-1] != "零":
                result += "零"
        return result.rstrip("零")


class WeatherService:
    def __init__(self, base_url="https://api.52vmy.cn/api/query/tian/three"):
        self.base_url = base_url

    def query_weather(self, city, info_type="weather"):
        try:
            url = f"{self.base_url}?city={urllib.parse.quote(city)}&type={info_type}"
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            try:
                return {"success": True, "city": city, "data": r.json()}
            except json.JSONDecodeError:
                return {"success": True, "city": city, "data": r.text}
        except Exception as e:
            return {"success": False, "city": city, "error": str(e)}


class NewsService:
    def __init__(self):
        self.api_url = "https://api.52vmy.cn/api/wl/60s/new"

    def get_news(self):
        try:
            r = requests.get(self.api_url, timeout=10)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        return None


class IPQueryService:
    def __init__(self):
        self.base_url = "https://api.52vmy.cn/api/query/itad/pro?ip="

    def query_ip(self, ip_address):
        try:
            url = self.base_url + urllib.parse.quote(ip_address)
            with urllib.request.urlopen(url, timeout=10) as resp:
                return resp.read().decode('utf-8')
        except Exception as e:
            return f"Error: {e}"
