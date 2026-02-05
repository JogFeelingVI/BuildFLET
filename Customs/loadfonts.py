# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-02-04 05:32:13
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-05 12:12:43

import pathlib as pl
from typing import Dict, Optional

class FontManager:
    """管理并自动生成 Flet 可用的字体映射表"""
    
    SUPPORTED_EXTENSIONS = {".ttf", ".otf", ".woff", ".woff2"}

    def __init__(self, fonts_subdir: str = "fonts"):
        """
        :param fonts_subdir: 相对于 assets 目录的字体文件夹路径
        """
        self.assets_path = self.__find_assets_dir()
        self.fonts_path = self.assets_path / fonts_subdir
        self.relative_prefix = fonts_subdir
        self.font_map: Dict[str, str] = self._generate_font_map()
        
    def __find_assets_dir(self):
        """尝试自动获取 assets 目录路径"""
        # 在 Flet 安卓环境中，通常脚本运行在根目录，assets 就在同级
        assets_path = pl.Path(__file__).parent.parent
        print(f'debug: {assets_path}')
        return assets_path / 'assets'

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