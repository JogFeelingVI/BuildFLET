# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-13 07:14:33
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-13 08:14:04

import flet as ft
import base64

def svgimage(number, stroke_color="#FFFFFF"):
    # SVG 模板：关键在于 text 标签的定位属性
    if isinstance(number, str):
        number = int(number)
    svg_code = f"""
    <svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
        <!-- 正圆边框:cx/cy 是圆心 r 是半径 -->
        <circle cx="100" cy="100" r="90" fill="none" stroke="{stroke_color}" stroke-width="8" />
        
        <!-- 居中数字 -->
        <text x="46" y="132"
              font-family="monospace" 
              font-size="100" 
              font-weight="bold"
              fill="{stroke_color}">
            {number:02d}
        </text>
    </svg>
    """
    # 转换为 Base64 给 Flet 使用
    b64_str = base64.b64encode(svg_code.encode("utf-8")).decode("utf-8")
    return b64_str