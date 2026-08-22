# -*- coding: utf-8 -*-
"""本地问答库管理（精确 + 模糊）"""

import json
import os
import re

from .config import QNA_DIR


class AnswerManager:
    """本地问答库管理（精确 + 模糊），数据实时写盘"""

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
