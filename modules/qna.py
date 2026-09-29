# -*- coding: utf-8 -*-
"""本地问答库管理（精确 + 模糊）"""

import json
import os
import re

from .config import QNA_DIR, ADMIN_IDS


class AnswerManager:
    """本地问答库管理（精确 + 模糊），数据实时写盘"""

    ADMIN_PREFIXES = ("精确问", "模糊问", "修改", "删问答", "列出", "清空所有问答")

    @classmethod
    def is_admin_command(cls, text):
        return text == "问答帮助" or text.startswith(cls.ADMIN_PREFIXES)

    def owns(self, text):
        return self.is_admin_command(text)

    def handle(self, text, ctx):
        return self.handle_admin(text, ctx.user_id)

    def __init__(self):
        self.precise_file = os.path.join(QNA_DIR, "precise_ans.json")
        self.fuzzy_file = os.path.join(QNA_DIR, "fuzzy_ans.json")
        self.precise = self._load(self.precise_file)
        self.fuzzy = self._load(self.fuzzy_file)

    def _load(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, dict) else {}
        except FileNotFoundError:
            self._save(path, {})
            return {}
        except Exception:
            return {}

    def _save(self, path, data):
        tmp = path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            os.replace(tmp, path)
        except Exception:
            pass

    def _get_bucket(self, fuzzy=False):
        if fuzzy:
            return self.fuzzy, self.fuzzy_file
        return self.precise, self.precise_file

    def clear_all_answers(self):
        self.precise, self.fuzzy = {}, {}
        self._save(self.precise_file, self.precise)
        self._save(self.fuzzy_file, self.fuzzy)
        return True

    def add_answer(self, question, answer, fuzzy=False):
        bucket, path = self._get_bucket(fuzzy)
        bucket[question.strip()] = answer.strip()
        self._save(path, bucket)
        return True

    def update_answer(self, question, new_answer):
        for bucket, path in (self.precise, self.precise_file), (self.fuzzy, self.fuzzy_file):
            if question in bucket:
                bucket[question] = new_answer.strip()
                self._save(path, bucket)
                return True
        return False

    def delete_answer(self, question):
        changed = False
        for bucket, path in (self.precise, self.precise_file), (self.fuzzy, self.fuzzy_file):
            if question in bucket:
                del bucket[question]
                self._save(path, bucket)
                changed = True
        return changed

    def all_data(self):
        data = dict(self.precise)
        data.update(self.fuzzy)
        return data

    def search(self, text):
        """返回精确或模糊匹配的答案"""
        if not text:
            return None
        # 精确匹配
        t = AnswerManager._norm(text)
        for q, a in self.precise.items():
            if AnswerManager._norm(q) == t:
                return a
        # 模糊匹配：key 作为连续整体出现
        tl = text.lower()
        best, best_score = None, 0
        for q, a in self.fuzzy.items():
            ql = q.lower()
            if ql == tl:
                score = 100 + len(q)
            elif ql in tl:
                score = 80 + len(q)
            else:
                score = 0
            if score > best_score:
                best_score, best = score, a
        return best

    @staticmethod
    def _norm(s):
        return re.sub(r'\s+', ' ', s).strip()

    def handle_admin(self, text, user_id):
        """问答管理命令（精确/模糊问答的增删改查），返回回复文本或 None"""
        is_admin = user_id in ADMIN_IDS
        if text == "问答帮助":
            return ("问答帮助：\n精确问 问题 答 答案（管理员）\n模糊问 问题 答 答案（管理员）\n"
                    "修改 原问题 答 新答案（管理员）\n删问答 问题（管理员）\n列出/清空（管理员）")
        if text.startswith("精确问") or text.startswith("模糊问"):
            if not is_admin:
                return "你没有权限添加问答"
            m = re.match(r"^(精确问|模糊问) (.+?) 答 (.+)$", text, re.DOTALL)
            if not m:
                return "格式：精确问/模糊问 问题 答 答案"
            kind, q, a = m.groups()
            self.add_answer(q, a, fuzzy=(kind == "模糊问"))
            return f"问答添加成功：\n问：{q.strip()}\n答：{a.strip()}"
        if text.startswith("修改"):
            if not is_admin:
                return "你没有权限修改问答"
            parts = text[2:].split("答", 1)
            if len(parts) == 2:
                if self.update_answer(parts[0].strip(), parts[1].strip()):
                    return f"修改成功：{parts[0].strip()}"
                return f"未找到问题：{parts[0].strip()}"
            return "格式：修改 原问题 答 新答案"
        if text.startswith("删问答"):
            if not is_admin:
                return "你没有权限删除问答"
            q = text[3:].strip()
            if not q:
                return "格式：删问答 问题"
            return "删除成功" if self.delete_answer(q) else "未找到该问题"
        if text.startswith("清空所有问答"):
            if not is_admin:
                return "你没有权限清空问答"
            self.clear_all_answers()
            return "问答已清空"
        if text.startswith("列出"):
            if not is_admin:
                return "你没有权限查看问答"
            data = self.all_data()
            if not data:
                return "还没有任何问答记录"
            return "当前问答（智能抽查10条）：\n" + "\n".join(f"问：{q}\n答：{a}" for q, a in
                                                                 list(data.items())[:10])
        return None
