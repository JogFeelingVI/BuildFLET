# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-02-04 05:32:13
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-05 04:18:02

import pathlib as pl
from typing import Dict, Optional

class FontManager:
    """管理并自动生成 Flet 可用的字体映射表"""
    
    SUPPORTED_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}

    def __init__(self, assets_dir: str, fonts_subdir: str = "fonts"):
        """
        :param assets_dir: Flet 的 assets 目录绝对路径
        :param fonts_subdir: 相对于 assets 目录的字体文件夹路径
        """
        self.assets_path = pl.Path(assets_dir)
        self.fonts_path = self.assets_path / fonts_subdir
        self.relative_prefix = fonts_subdir
        self.font_map: Dict[str, str] = self._generate_font_map()

    def _generate_font_map(self) -> Dict[str, str]:
        fonts = {}
        if not self.fonts_path.exists() or not self.fonts_path.is_dir():
            print(f"Warning: Font directory not found at {self.fonts_path}")
            return fonts

        for file in self.fonts_path.iterdir():
            if file.is_file() and file.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                # 优化 Key 的生成逻辑：
                # 如果是 "Roboto-Bold.ttf"，Key 设为 "Roboto-Bold" 
                # 这样可以精确控制不同字重
                font_family_key = file.stem 
                
                # Flet 需要的是相对于 assets 目录的路径
                # 例如: "fonts/Roboto-Bold.ttf"
                fonts[font_family_key] = f"{self.relative_prefix}/{file.name}"
        
        return fonts

    def get_fonts(self):
        return self.font_map