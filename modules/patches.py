# -*- coding: utf-8 -*-
"""对 qq-botpy 的兼容性补丁。"""

from botpy.connection import ConnectionState
from botpy.message import GroupMessage


def apply_group_message_patch():
    """qq-botpy 1.2.1 未内置「群全量消息（免@）」事件解析，这里补上。

    平台需在群设置中允许机器人接收全部消息，事件才会推送（Intent 同为 1<<25）。
    """
    def _parse_group_message_create(self, payload):
        _message = GroupMessage(self.api, payload.get("id", None), payload.get("d", {}))
        self._dispatch("group_message_create", _message)

    ConnectionState.parse_group_message_create = _parse_group_message_create
