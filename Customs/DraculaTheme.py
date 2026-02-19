# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 04:20:46
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-19 13:23:02
from typing import Final
import random
import colorsys


class DraculaColors:
    """定义德古拉配色方案"""

    BACKGROUND: Final[str] = "#282a36"
    CURRENT_LINE: Final[str] = "#44475a"
    FOREGROUND: Final[str] = "#f8f8f2"
    COMMENT: Final[str] = "#6272a4"
    PURPLE: Final[str] = "#bd93f9"
    PINK: Final[str] = "#ff79c6"
    CYAN: Final[str] = "#8be9fd"
    GREEN: Final[str] = "#50fa7b"
    ORANGE: Final[str] = "#ffb86c"
    RED: Final[str] = "#ff5555"
    YELLOW: Final[str] = "#f1fa8c"
    CRADBG: Final[str] = "#1e293b"


def RandColor(mode="def"):
    """生成随机颜色, mode 可选 'def'（默认）或 'Morandi' 'Neon' 'Glass'"""
    h = random.random()  # 色相 (Hue)
    s = random.uniform(0.4, 1.0)  # 饱和度 (Saturation)
    l = random.uniform(0.4, 0.8)  # 亮度 (Lightness)，避免过黑或过白

    match mode:
        case "Morandi":
            s = random.uniform(0.2, 0.5)  # Morandi 色系通常较柔和，饱和度较低
            l = random.uniform(0.5, 0.7)  # Morandi 色系亮度适中
        case "Neon":
            s = random.uniform(0.7, 1.0)  # Neon 色系通常非常鲜艳，饱和度较高
            l = random.uniform(0.5, 0.7)  # Neon 色系亮度适中，避免过暗
        case "Glass":
            s = random.uniform(0.3, 0.6)  # Glass 色系通常较柔和，饱和度适中
            l = random.uniform(0.5, 0.8)  # Glass 色系亮度较高，模拟玻璃质感
        case _:
            pass  # 使用默认的 HSL 范围

    # 2. HSL 转换为 RGB (colorsys 中使用 HLS，顺序略有不同)
    # 注意：colorsys.hls_to_rgb 接收的顺序是 (h, l, s)
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    # 3. 将 0-1 范围的 RGB 转换为 0-255 并转为 Hex 格式
    hex_color = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    return hex_color
