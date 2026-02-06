# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-02-04 05:32:13
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-06 06:50:16


import requests
import pathlib
import concurrent.futures
import time
from typing import Dict, Optional

#region FontManager
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
        assets_path = pathlib.Path(__file__).parent.parent
        print(f"debug: {assets_path}")
        return assets_path / "assets"

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
#endregion
    

#region FastSourcePicker
class FastSourcePicker:
    def __init__(self):
        self.sources = [
            "https://gitee.com/jogfeelingvi/lotter_resource/raw/main/fonts.json",
            "https://github.com/JogFeelingVI/lotter_resource/raw/refs/heads/main/fonts.json"
        ]
        self.storage_path = self.__storage_path()
    
    def __storage_path(self):
        storage_temp = pathlib.Path(__file__).parent.parent / "storage/temp"
        storage_temp.mkdir(parents=True, exist_ok=True)
        print(f'debug storage_temp {storage_temp}')
        return storage_temp

    def _fetch_json(self, url):
        """单个请求的任务"""
        try:
            # 设置较短的 timeout，如果 5 秒都没响应直接放弃
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                print(f"Successfully retrieved data from the source: {url}")
                return response.json(),url
        except Exception as e:
            print(f"Request to source {url} failed: {e}")
        return None
    
    def __dFont(self, name, filepath, url):
        try:
            # 设置较短的 timeout，如果 5 秒都没响应直接放弃
            response = requests.get(url, timeout=5)
            fulpath:pathlib.Path = self.storage_path / filepath
            fulpath.touch(mode=438, exist_ok=True)
            print(f'{fulpath=}')
            if response.status_code == 200:
                with open(fulpath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                    
                    # return {name:self.storage_path / }
        except Exception as e:
            print(f"Request to source {url} failed: {e}")
        return None
    
    def __Correction_parameters(self, result) -> dict[str,str]:
        font_map, source_url = result
        # 显式转换确保类型安全 (如果 result 里的内容不确定)
        font_dict = dict(font_map)
        url_str = str(source_url)
        for name, fontpath in font_dict.copy().items():
            if not f'{name}'.startswith("--"):
                font_dict[name] = url_str.replace("/fonts.json", fontpath)
                # self.__dFont(name, fontpath, font_dict[name] )
                print(f'{font_dict[name]}')
                
            # else:
                font_dict.pop(name)
        return font_dict

    def __download_fonts(self, fonts_dict:dict):
        fontLocal = fonts_dict.copy()
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(fontLocal.values())) as executor:
            future_to_url = {executor.submit(self.__dFont, name, url): url for name,url in fontLocal.items()}
        
    def get_fastest_json(self):
        """并行执行，取最快的结果"""
        # 使用线程池并发请求
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.sources)) as executor:
            # 提交所有任务
            future_to_url = {executor.submit(self._fetch_json, url): url for url in self.sources}
            
            # 等待第一个任务完成
            # return_when=FIRST_COMPLETED 意味着只要有一个成功就继续
            done, not_done = concurrent.futures.wait(
                future_to_url.keys(), 
                timeout=10, # 总等待限时
                return_when=concurrent.futures.FIRST_COMPLETED
            )

            # 遍历已完成的任务
            for future in done:
                result = future.result()
                if result:
                    # 只要拿到了有效的 JSON，就尝试取消其他还在进行的任务并返回结果
                    for unfinished in not_done:
                        unfinished.cancel()
                    return self.__Correction_parameters(result)

        print("All sources are inaccessible.")
        return None
#endregion
