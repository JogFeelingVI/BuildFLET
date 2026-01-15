# -*- coding: utf-# -*-
# @Author: JogFeelingVI
# @Date:   #-#-# #:#:#
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-14 07:01:53

import re
import time
import flet as ft
from itertools import product

# Tail, head
__tailparameters = [
    ">#",
    "># --z",
    "># --w",
    "># --h",
    "># --m#",
    "<#",
    "<# --z",
    "<# --h",
    "<# --w",
    "<# --m#",
    #
    "range #,#",
    "range #,# --z",
    "range #,# --h",
    "range #,# --w#",
    "range #,# --m#",
]

__headparameters = [
    "bit#",
    "bit#,#",
    "mod#",
]

__single_rule = [
    "#,#,#,#,#,#,#",
    "#,#,#,#",
    "#,#",
    "#,#,#",
    # bitN >,<
    ">#",
    "># --z",
    "># --w",
    "># --h",
    "># --m#",
    "<#",
    "<# --z",
    "<# --h",
    "<# --w",
    "<# --m#",
    # range
    "range #,#",
    "range #,# --z",
    "range #,# --h",
    "range #,# --w#",
    "range #,# --m#",
]


def combination_rule():
    """组合头部参数和尾部参数 用来测试所有命令行"""
    for i in __single_rule:
        ri = i.replace("#", "1")
        yield ri
    combin = product(__headparameters, __tailparameters)
    for h, t in combin:
        ri = f"{h} {t}".replace("#", "1")
        yield ri


class Tokenizer:
    """优化后的分词着色类"""

    def __init__(self):
        # 这里的顺序很重要，长匹配应放在短匹配前面
        self.token_defs = {
            "range": [r"range\s\d+(?:,\d+)?", "#bd93f9"],  # PURPLE
            "bit": [r"bit\d+(?:,\d+)?", "#ff79c6"],  # PINK
            "mod": [r"mod\d+", "#ff79c6"],  # PINK
            "dayu09": [r">\d+", "#6272a4"],  # COMMENT
            "xiaoyu09": [r"<\d+", "#6272a4"],  # COMMENT
            "zhjo": [r"[-]{2}[zhjo]", "#8be9fd"],  # CYAN
            "mod3": [r"[-]{2}m\d+", "#50fa7b"],  # GREEN
            "wei": [r"[-]{2}w\d+", "#ffb86c"],  # ORANGE
        }

        # 核心：将所有正则合并为一个巨大的正则，并使用命名分组 (?P<name>...)
        regex_parts = []
        for name, (pattern, color) in self.token_defs.items():
            regex_parts.append(f"(?P<{name}>{pattern})")

        # 加上对空格和普通文本的捕获，确保不丢失内容
        self.master_regex = re.compile("|".join(regex_parts))

    def Segment(self, word: str):
        if not word:
            return []

        result = []
        last_index = 0

        # 使用 finditer 一次性扫描
        for match in self.master_regex.finditer(word):
            # 1. 检查当前匹配项和上一个匹配项之间是否有“未定义”的普通文本（如空格）
            if match.start() > last_index:
                unmatched_text = word[last_index : match.start()]
                result.append((unmatched_text, None))  # None 代表使用默认颜色

            # 2. 获取当前匹配到的分组名称和内容
            token_type = match.lastgroup
            token_text = match.group(token_type)
            color = self.token_defs[token_type][1]

            result.append((token_text, color))
            last_index = match.end()

        # 3. 检查是否有剩余未匹配的尾部文本
        if last_index < len(word):
            result.append((word[last_index:], None))

        return result


# def main():
#     token = Tokenizer()
#     for i in combination_rule():
#         segment = token.Segment(i)
#         if segment:
#             print(f"main {i} {segment}")


# if __name__ == "__main__":
#     ta = time.perf_counter()
#     main()
#     tb = time.perf_counter()
#     print(f"time: {tb - ta:.6f}sec")
