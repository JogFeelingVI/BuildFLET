# -*- coding: utf-# -*-
# @Author: JogFeelingVI
# @Date:   #-#-# #:#:#
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-11 14:58:49

from importlib.util import source_from_cache
import re
from difflib import SequenceMatcher
from itertools import product,islice
from flet import AutoCompleteSuggestion as ACS

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
    """组合头部参数和尾部参数"""
    combin = product(__headparameters, __tailparameters)
    for h, t in combin:
        yield f"{h} {t}"


def __get_structure(text):
    """
    提取语法结构：转小写并把数字替换为 #
    只用于用户输入
    例如: "Choose 6 from 33" -> "choose # from ##"
    """
    text = text.lower()
    return re.sub(r"\d+", "#", text)


def __calc_similarity(a: str, b: str):
    """
    计算两个字符串的相似度分数
    a 用户输入
    b 计算机AI预测
    """
    return SequenceMatcher(None, a, b).ratio()


def cale_score(user_input, scored_suggestions, source):
    user_raw = __get_structure(user_input)
    for template in source:
        struct_score = __calc_similarity(user_raw, template)
        raw_score = __calc_similarity(user_input.lower(), template.lower())
        final_score = (struct_score * 0.7) + (raw_score * 0.3)
        if final_score > 0.5:
            scored_suggestions.append((final_score, template))


# Predicting user input
def AI_gen_sugguest(user_input: str):
    scored_suggestions = []
    cale_score(user_input, scored_suggestions, __single_rule)
    cale_score(user_input, scored_suggestions,  islice(combination_rule(), 1000) )
    if not scored_suggestions:
        return []
    scored_suggestions.sort(key=lambda x: x[0], reverse=True)
    format_list = []
    for _, ai_string in scored_suggestions[0:5]:
        format_list.append(
            # {"key":user_input, "value":ai_string}
            ACS(key=user_input, value=ai_string)
        )

    return format_list or []


if __name__ == "__main__":
    AI_gen_sugguest("bit3,")
