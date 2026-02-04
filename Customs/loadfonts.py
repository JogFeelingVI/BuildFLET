# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-02-04 05:32:13
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-04 12:22:01

import re
import pathlib as pl


class GenerateFontList:
    font_extensions = {".ttf", ".otf"}

    def __init__(self, fontPath: str):
        self.fontdict = self.__Detection_Path(fontPath)

    def __Detection_Path(self, fontPath: str):
        if not fontPath:
            return None
        path = pl.Path(fontPath)
        if not path.exists():
            return None
        # 遍历目录并根据后缀过滤
        font_files = {
            f.stem.split("-")[0].split("_")[0]: f"/fonts/{f.name}"
            for f in path.iterdir()
            if f.is_file() and f.suffix.lower() in self.font_extensions
        }
        return font_files
