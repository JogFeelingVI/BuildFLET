# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-04-11 06:15:53
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-14 22:34:27

import io
import time
import fitz
from typing import Any

from PIL import Image, ImageColor, ImageDraw, ImageFont
try:
    from .DraculaTheme import RandColor
    from .loadfonts import FontManager
except:
    from DraculaTheme import RandColor
    from loadfonts import FontManager


# renion
def displayinfo(msg: Any, verbose: int = 1, **kwargs):
    """
    display info
    """
    level = kwargs.get("level", 0)
    time_format = kwargs.get("time_format", "%Y-%m-%d %H:%M:%S")
    msg_format = kwargs.get("msg_format", "{t} | {msg}")
    time_log = time.strftime(time_format, time.localtime())
    if level >= verbose:
        print(msg_format.format(t=time_log, msg=f"{msg}"))


# endregion


# region Imagers
class Imagers:
    @staticmethod
    def TextBackground(**kwargs) -> bytes:
        """
        ## Rounded rectangle parameters
        - height: int | float = 200,
        - width: int | float = 400,
        - fill: str = "#FF0000",
        - stroke_width: int | float = 3,
        - stroke="#ffffff",
        - opacity: float = 0.6,
        - rx: int | float = 8,
        ### return
        - bytes
        """
        height = kwargs.get("height", 200)
        width = kwargs.get("width", 400)
        fill = kwargs.get("fill", "#FF0000")
        stroke_width = kwargs.get("stroke_width", 3)
        stroke = kwargs.get("stroke", "#ffffff")
        opacity = kwargs.get("opacity", 1.0)
        rx = kwargs.get("rx", 8)
        svgcode = f"""
        <svg width="{width + stroke_width * 2}" height="{height + stroke_width * 2}" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
        <!-- Created with SVG-edit - https://github.com/SVG-Edit/svgedit-->
        <rect fill="{fill}" height="{height}" rx="{rx}" ry="{rx}" opacity="{opacity}" stroke="{stroke}" stroke-width="{stroke_width}" width="{width}" x="{stroke_width}" y="{stroke_width}"/>
        </svg>
        """
        return svgcode.encode("utf-8")

    @staticmethod
    def Background(**kwargs) -> bytes:
        """
        ## Create a background of specified size
        - height: int | float = 200,
        - width: int | float = 400,
        - fill: str = "#44475a",
        ### return
        - bytes
        """
        height = kwargs.get("height", 200)
        width = kwargs.get("width", 400)
        fill = kwargs.get("fill", "#FF0000")
        svgcode = f"""
        <svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg" xmlns:svg="http://www.w3.org/2000/svg">
        <!-- Created with SVG-edit - https://github.com/SVG-Edit/svgedit-->
        <rect fill="{fill}" height="{height}" id="svg_1" stroke="#ffffff" stroke-width="0" width="{width}" x="0" y="0"/>
        </svg>
        """
        return svgcode.encode("utf-8")

    @staticmethod
    def TextToImage(**kwargs) -> Image:
        """
        ## Text to picture
        - ***fontmap: dict***
        - name: str = "RacingSansOne-Regular" 使用 fontmap 里的名字
        - text: str = "Jackpot Lotter"
        - textsize: int = 48
        - text_color: str = "#d24141"
        - stroke: str = "#FFFFFF"
        - stroke_width: int = 0
        - opacity: float = 1
        - spacing: int = 4
        - text_align: align
        - max_width:int *`AUTO`*
        ### return
        - Image
        """
        fontmap = kwargs.get("fontmap", None)
        name = kwargs.get("name", "RacingSansOne-Regular")
        text = kwargs.get("text", "Jackpot Lotter")
        textsize = kwargs.get("textsize", 48)
        text_color = kwargs.get("text_color", "#FF0000")
        stroke_width = kwargs.get("stroke_width", 0)
        stroke = kwargs.get("stroke", "#ffffff")
        opacity = kwargs.get("opacity", 1.0)
        spacing = kwargs.get("spacing", 4)
        # 文字内部对齐方式: left, center, right
        text_align = kwargs.get("align", "left")
        # 1. 找到对应的本地字体文件路径
        max_width = kwargs.get("max_width", None)
        try:
            r, g, b = ImageColor.getrgb(text_color)[:3]
            text_color = (r, g, b, int(opacity * 255))
            sr, sg, sb = ImageColor.getrgb(stroke)[:3]
            stroke = (sr, sg, sb, int(opacity * 255))
        except ValueError:
            text_color = text_color  # 容错处理
            stroke = stroke
        font_path = fontmap.get(name)
        # 2. 加载字体
        font = ImageFont.truetype(font_path, textsize)
        if max_width:
            # 这里的 max_width 应该减去一点安全边距
            text = Imagers.auto_wrap_text(text, font, max_width)
        temp_img = Image.new("RGBA", (1, 1))
        temp_draw = ImageDraw.Draw(temp_img)
        # 获取多行文本的边界: (left, top, right, bottom)
        bbox = temp_draw.multiline_textbbox(
            (stroke_width, stroke_width),
            text,
            font=font,
            stroke_width=stroke_width,
            spacing=spacing,
            align=text_align,
        )
        left, top, right, bottom = bbox
        # if left < 0:
        #     left = left - left
        #     top = top -left
        #     right = right + left
        #     top = top + left
        width = right - left + 10
        height = bottom - top + 10
        # 3. 绘制
        img = Image.new("RGBA", (int(width), int(height)), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        # 使用 multiline_text 进行绘制
        draw.multiline_text(
            (5 - left, 5 - top),
            text,
            font=font,
            fill=text_color,
            stroke_width=stroke_width,
            stroke_fill=stroke,
            spacing=spacing,
            align=text_align,  # 这决定了多行之间如何对齐
        )
        return img

    @staticmethod
    def CircleNumber(**kwargs) -> Image:
        """
        生成一个带数字的圆圈
        参数:
        - size: int (圆圈直径)
        - fill: str (圆圈填充颜色)
        - stroke: str (边框颜色)
        - stroke_width: int
        - text: str/int (1-99)
        - text_color: str
        - fontmap, name (字体相关)
        - font_size_ratio: float (字号占圆圈直径的比例，默认 0.6)
        - opacity: float 0.6
        """
        size = kwargs.get("size", 60)
        fill = kwargs.get("fill", "#FF0000")
        stroke = kwargs.get("stroke", "#FFFFFF")
        stroke_width = kwargs.get("stroke_width", 2)
        text = str(kwargs.get("text", "1"))
        text_color = kwargs.get("text_color", "#FFFFFF")
        opacity = kwargs.get("opacity", 0.6)
        try:
            r, g, b = ImageColor.getrgb(fill)[:3]
            fill = (r, g, b, int(opacity * 255))
            sr, sg, sb = ImageColor.getrgb(stroke)[:3]
            stroke = (sr, sg, sb, int(opacity * 255))
        except ValueError:
            fill = fill  # 容错处理
            stroke = stroke
        # 为了防止边框切边，画布稍微大一点点
        img_size = size + stroke_width * 2
        img = Image.new("RGBA", (img_size, img_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # 2. 画圆
        # 边界计算：[左上角x, 左上角y, 右下角x, 右下角y]
        shape_pos = [
            stroke_width,
            stroke_width,
            size + stroke_width,
            size + stroke_width,
        ]
        draw.ellipse(shape_pos, fill=fill, outline=stroke, width=stroke_width)

        # 3. 画数字
        # 动态计算字号：默认文字高度为圆圈直径的 60%
        font_path = kwargs.get("fontmap").get(kwargs.get("name"))
        font_size = int(size * kwargs.get("font_size_ratio", 0.7))
        font = ImageFont.truetype(font_path, font_size)

        # 使用 anchor="mm" 实现完美的正中心对齐
        # 坐标选在画布的中心点
        center_pos = (img_size / 2, img_size / 2)

        draw.text(
            center_pos,
            text,
            fill=text_color,
            font=font,
            anchor="mm",  # m=middle (水平居中), m=middle (垂直居中)
        )

        return img

    @staticmethod
    def bytestoPNG(svgcode: bytes) -> Image:
        """
        ## Byte to image
        - TextBackground (func)
        - Background (func)
        ### Convert to png image
        - Image
        """
        pix = fitz.open("svg", svgcode)[0].get_pixmap(dpi=72, alpha=True)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        return img

    @staticmethod
    def auto_wrap_text(text, font, max_width):
        """
        根据像素宽度自动给文本添加换行符
        """
        lines = []
        # 如果包含现有的换行符，先拆分处理
        for paragraph in text.split("\n"):
            line = ""
            for word in paragraph.split(" "):
                test_line = line + (" " if line else "") + word
                if font.getlength(test_line) <= max_width:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            lines.append(line)
        return "\n".join(lines)


# endregion


# renion Rendering
class Rendering:
    def __init__(self, **kwargs):
        """单位统一为px"""
        self.padding = kwargs.get("padding", 20)
        self.width = kwargs.get("width", 400)
        self.height = kwargs.get("height", 888)
        self.bgcolor = kwargs.get("bgcolor", (255, 255, 255, 0))
        self.fontsManager = FontManager()
        self.__fonts_map = self.fontsManager.fonts_map(abs=True)
        self.canvas = Image.new("RGBA", (self.width, self.height), self.bgcolor)
        # 3. Y轴布局游标（记录当前画到了哪个高度）
        # 初始高度留出顶部的 padding
        self.current_y = self.padding
        self.kwargs = kwargs

    # ==========================================
    # 核心装配引擎（私有方法）
    # ==========================================
    def _paste_element(
        self,
        element_img: Image.Image,
        align: str = "center",
        margin_bottom: int = 20,
        expand: bool = False,
    ):
        """
        核心装配引擎
        - expand: True 表示强制放大到最大宽度；False 表示仅在超过时缩小
        """
        # 1. 计算允许的最大宽度
        max_allowed_width = self.width - (self.padding * 2)
        # 2. 缩放逻辑
        # 情况 A: 零件太宽了，必须缩小 (无论 expand 是什么)
        # 情况 B: 零件太窄了，且开启了 expand 强制放大
        if element_img.width > max_allowed_width or (
            expand and element_img.width < max_allowed_width
        ):
            ratio = max_allowed_width / element_img.width
            new_height = int(element_img.height * ratio)
            # 使用 LANCZOS 保持高质量缩放
            element_img = element_img.resize(
                (max_allowed_width, new_height), Image.LANCZOS
            )
            displayinfo(
                msg=f"ℹ️ Info: Element has been scaled to {max_allowed_width}px (ratio: {ratio:.2f})",
                verbose=2,
                **self.kwargs,
            )

        # 2. 【核心修改】动态检查高度是否足够
        # 需要的高度 = 当前位置 + 零件高度 + 下边距
        needed_h = self.current_y + element_img.height + margin_bottom
        self._expand_canvas(needed_h)

        # 3. 计算 X 坐标 (如果已经 expand 了，其实 x 永远等于 self.padding)
        if align == "center":
            x = (self.width - element_img.width) // 2
        elif align == "right":
            x = self.width - element_img.width - self.padding
        else:  # left
            x = self.padding
        # 4. 粘贴 (使用 alpha_composite 保持半透明层级正确)
        if element_img.mode != "RGBA":
            element_img = element_img.convert("RGBA")
        temp_layer = Image.new("RGBA", self.canvas.size, (0, 0, 0, 0))
        temp_layer.paste(element_img, (x, self.current_y))
        self.canvas = Image.alpha_composite(self.canvas, temp_layer)
        # 更新 Y 坐标游标
        self.current_y += element_img.height + margin_bottom

    def _expand_canvas(self, required_height):
        """私有方法：动态增加画布高度"""
        if required_height > self.canvas.height:
            # 创建新画布，高度为需求高度（可以额外加点 buffer 减少频繁扩容）
            new_height = required_height + 200
            new_canvas = Image.new("RGBA", (self.width, new_height), self.bgcolor)
            # 将旧内容贴到新画布
            new_canvas.paste(self.canvas, (0, 0))
            self.canvas = new_canvas
            displayinfo(
                msg=f"🚀 Canvas expanded to {new_height}px", verbose=2, **self.kwargs
            )

    def add_spacing(self, **kwargs):
        """
        ### 添加空白控件
        #### kwargs
        - height:int 默认 10
        """
        height = kwargs.get("height", 10)
        self.current_y += height
        return self

    # ==========================================
    # 暴露给外部的 API 接口
    # ==========================================
    def set_background(self, **kwargs):
        """
        ### 画背景
        #### kwargs
        - fill:str = #000000
        - opacity:float = 1.0
        """
        fill = kwargs.get("fill", "#000000")
        opacity = kwargs.get("opacity", 1.0)
        self.bgcolor = fill
        try:
            r, g, b = ImageColor.getrgb(fill)[:3]
            fill = (r, g, b, int(opacity * 255))
        except ValueError:
            fill = fill
        bg = Image.new("RGBA", (self.width, self.height), self.bgcolor)
        self.canvas.paste(bg, (0, 0))
        return self

    def add_title(self, **kwargs):
        """
        ### 画标题
        #### kwargs
        - expand: bool = False
        - align: str = center
        - margin_bottom: int = 30
        - fontmap:dict = self.__fonts_map *`AUTO`*
        - textsize:int = 48
        - name: str = `RacingSansOne-Regular`
        - max_width:int *`auto`*
        """
        expand = kwargs.pop("expand", False)
        align = kwargs.pop("align", "center")
        margin_bottom = kwargs.pop("margin_bottom", 30)
        # 2. 补全 TextToImage 缺少的强制参数（例如 fontmap）
        # 这样 add_title 调用者就不需要自己传 fontmap 了
        kwargs["fontmap"] = self.__fonts_map
        # 3. 设置标题的默认样式（如果调用者没传的话）
        kwargs.setdefault("textsize", 48)
        kwargs.setdefault("name", "RacingSansOne-Regular")
        if "max_width" not in kwargs:
            kwargs["max_width"] = self.width - (self.padding * 2)
        title_img = Imagers.TextToImage(**kwargs)
        self._paste_element(
            title_img, align=align, margin_bottom=margin_bottom, expand=expand
        )
        return self

    def add_circle_number(self, **kwargs):
        """
        在画布上添加一个圆形数字
        """
        align = kwargs.pop("align", "center")
        margin_bottom = kwargs.pop("margin_bottom", 20)
        # 补全必要参数
        kwargs["fontmap"] = self.__fonts_map
        kwargs.setdefault("name", "RacingSansOne-Regular")
        # 生成图片
        circle_img = Imagers.CircleNumber(**kwargs)
        # 装配
        self._paste_element(circle_img, align=align, margin_bottom=margin_bottom)
        return self

    def add_text(self, **kwargs):
        """画文字"""
        # 模拟生成
        expand = kwargs.pop("expand", False)
        align = kwargs.pop("align", "left")
        margin_bottom = kwargs.pop("margin_bottom", 30)
        kwargs["fontmap"] = self.__fonts_map
        # 3. 设置标题的默认样式（如果调用者没传的话）
        kwargs.setdefault("textsize", 48)
        kwargs.setdefault("name", "RacingSansOne-Regular")
        if "max_width" not in kwargs:
            kwargs["max_width"] = self.width - (self.padding * 2)
        text_img = Imagers.TextToImage(**kwargs)
        self._paste_element(
            text_img, align=align, margin_bottom=margin_bottom, expand=expand
        )
        return self

    def add_text_with_bg(self, **kwargs):
        """
        ## Draw text with a background (e.g. labels, button styles)
        - align align
        - margin_bottom 25
        - padding_x 15
        - padding_x 10
        - bg_fill #FF0000
        - bg_stroke  #ffffff
        - bg_stroke_width 3
        - bg_rx 8
        - bg_opacity 0.1
        """
        # 1. 提取布局和间距参数
        expand = kwargs.pop("expand", False)
        align = kwargs.pop("left", "center")
        margin_bottom = kwargs.pop("margin_bottom", 25)
        px = kwargs.pop("padding_x", 10)  # 左右内边距
        py = kwargs.pop("padding_y", 10)  # 上下内边距

        # 2. 提取并分离背景参数 (以 bg_ 开头)
        bg_params = {
            "fill": kwargs.pop("bg_fill", "#FF0000"),
            "stroke": kwargs.pop("bg_stroke", "#ffffff"),
            "stroke_width": kwargs.pop("bg_stroke_width", 2),
            "rx": kwargs.pop("bg_rx", 10),
            "opacity": kwargs.pop("bg_opacity", 1.0),
        }

        # 3. 生成文字图片 (此时 kwargs 剩下的都是文字参数)
        kwargs["fontmap"] = self.__fonts_map
        if "max_width" not in kwargs:
            kwargs["max_width"] = self.width - (self.padding * 2)
        text_img = Imagers.TextToImage(**kwargs)
        # 4. 计算背景框的尺寸
        # 背景宽 = 文字宽 + 左右 padding
        # 背景高 = 文字高 + 上下 padding
        bg_w = text_img.width + (px * 2)
        bg_h = text_img.height + (py * 2)
        # 5. 生成背景图片
        bg_params["width"] = bg_w
        bg_params["height"] = bg_h
        bg_svg_code = Imagers.TextBackground(**bg_params)
        bg_img = Imagers.bytestoPNG(bg_svg_code)
        # 6. 合成文字与背景
        # 创建一个能容纳背景的临时透明画布
        # 注意：bg_img 经过 bytestoPNG 裁切后，尺寸可能因描边微调，以实际为准
        tag_canvas = Image.new("RGBA", (bg_img.width, bg_img.height), (0, 0, 0, 0))
        # 先贴背景
        tag_canvas.paste(bg_img, (0, 0), bg_img)
        # 再贴文字 (居中对齐)
        tx = (tag_canvas.width - text_img.width) // 2
        ty = (tag_canvas.height - text_img.height) // 2
        # 文字也需要通过一个临时层叠加，防止文字的抗锯齿边缘把背景“挖透”
        temp_text_layer = Image.new("RGBA", tag_canvas.size, (0, 0, 0, 0))
        temp_text_layer.paste(text_img, (tx, ty))
        tag_canvas = Image.alpha_composite(tag_canvas, temp_text_layer)

        self._paste_element(
            tag_canvas, align=align, margin_bottom=margin_bottom, expand=expand
        )
        return self

    def Trim_Invalid_Space(self) -> Image:
        """
        修剪图片
        """
        final_height = self.current_y - 0 + self.padding
        # 防止高度越界（如果 padding 很大或者没内容时）
        final_height = min(final_height, self.canvas.height)
        # 裁切画布：从 (0,0) 到 (宽, 当前游标位置+padding)
        final_img = self.canvas.crop((0, 0, self.width, int(final_height)))
        displayinfo(
            msg=f"✅ Trim_Invalid_Space: ({self.width}x{int(final_height)}px)",
            verbose=1,
            **self.kwargs,
        )
        return final_img

    def Write_to_file(self, **kwargs):
        """
        ### 保存文件
        #### 参数
        - filepath:str 默认值 ./Lotter_Rendering.png
        """
        filepath: str = kwargs.get("filepath", "./Lotter_Rendering.png")
        # 我们希望底部也保留和顶部一样的 padding
        final_img = self.Trim_Invalid_Space()
        final_img.save(filepath)

    def RetrieveImage(self) -> Image:
        """
        ### 获取图像
        #### 无参数
        #### 返回对象 Image
        """
        return self.Trim_Invalid_Space()

    def RetrieveBytes(self) -> bytes:
        ### 获取图像的二进制
        #### 无参数
        #### 返回对象 bytes
        img_byte_arr = io.BytesIO()
        img_obj = self.Trim_Invalid_Space()
        img_obj.save(img_byte_arr, format="PNG")  # 将图片以 PNG 格式写入内存
        return img_byte_arr.getvalue()


# endregion




# 一下是测试程序
def test_Rendering():
    renderer = Rendering(width=400 * 2, height=888 * 2, padding=30, level=10)
    (
        renderer.set_background(fill="#1A2F45", opacity=1)
        .add_title(
            text="Today’s super jackpot",
            name="RacingSansOne-Regular",
            textsize=60,
            text_color="#FFD000",
        )
        .add_text_with_bg(
            text="01 05 08 10 11 16 17 18 20 56 78 90",  # 文字内容
            name="Inter_18pt-SemiBold",  # 字体
            textsize=50,  # 字号
            text_color="#ffffff",  # 文字颜色
            padding_x=10,  # 左右撑开 40px
            padding_y=10,
            stroke_width=0.2,  # 上下撑开 20px
            bg_fill="#5b50fa",  # 背景颜色（绿色）
            bg_rx=8,  # 大圆角
            bg_stroke="#ffffff",  # 白色边框
            bg_stroke_width=0,
            bg_opacity=0.9,
            margin_bottom=10,
            expand=True,  # 下方留白
        )
        .add_text_with_bg(
            text="01 05 08 10 11 16 17 18 20 56 78 90",  # 文字内容
            name="Inter_18pt-SemiBold",  # 字体
            textsize=30,  # 字号
            text_color="#ffffff",  # 文字颜色
            padding_x=10,  # 左右撑开 40px
            padding_y=10,  # 上下撑开 20px
            stroke_width=1,
            bg_fill="#6b29ce",  # 背景颜色（绿色）
            bg_rx=8,  # 大圆角
            bg_stroke="#ffffff",  # 白色边框
            bg_stroke_width=1,
            bg_opacity=0.8,
            margin_bottom=10,  # 下方留白
            expand=True,
        )
        .add_spacing(20)
        .add_circle_number(
            align="left",
            text="1",
            size=45,
            fill="#FF0000",  # 金色
            text_color="#FFFF00",  # 黑色字
            stroke="#FFFFFF",
            stroke_width=0,
            opacity=0.8,
        )
        .add_text_with_bg(
            text="01 05 08 10 11 + 17 18",  # 文字内容
            name="Inter_18pt-SemiBold",  # 字体
            textsize=30,  # 字号
            text_color="#ffffff",  # 文字颜色
            padding_x=10,  # 左右撑开 40px
            padding_y=10,  # 上下撑开 20px
            stroke_width=1,
            bg_fill="#df692e",  # 背景颜色（绿色）
            bg_rx=8,  # 大圆角
            bg_stroke="#ffffff",  # 白色边框
            bg_stroke_width=0.4,
            bg_opacity=0.6,
            margin_bottom=10,  # 下方留白
            expand=True,
        )
        .add_text(text="God is here", align="left", textsize=28)
        .add_text_with_bg(
            index=1,
            text="01 05 08 10 11 17 + 18",  # 文字内容
            name="Inter_18pt-SemiBold",  # 字体
            textsize=30,  # 字号
            text_color=RandColor(mode="neon"),  # 文字颜色
            padding_x=10,  # 左右撑开 40px
            padding_y=10,  # 上下撑开 20px
            stroke_width=0,
            bg_fill=RandColor(mode="neon"),  # 背景颜色（绿色）
            bg_rx=3,  # 大圆角
            bg_stroke=RandColor(mode="neon"),  # 白色边框
            bg_stroke_width=0,
            bg_opacity=0.6,
            margin_bottom=10,  # 下方留白
            expand=True,
        )
        .add_text(
            text="Activity rules:\n1. Participate in the lottery\n2. Get rewards\n3. 祝您中的大奖\n4. 宝くじが当たりますように！",
            name="NotoSansSC-Regular",
            textsize=24,
            align="left",
            stroke_width=0,
            text_color=RandColor(mode="neon"),
            opacity=1,
        )
        .Write_to_file("./final_poster.png")
    )


def test_text():
    fm = FontManager()
    imgs = Imagers()
    fontmap = fm.fonts_map(abs=True)
    text = imgs.TextToImage(fontmap=fontmap, text="JogFeelingCLI", textsize=48)
    text.Write_to_file("./textpng.png")


def test_svgtopng():
    imgs = Imagers()
    svg = imgs.TextBackground()
    svgpng = imgs.bytestoPNG(svg)
    svgpng.Write_to_file("./svgtopng.png")


def test_log_list():
    style_conf = {
        "background": {"fill": "#1A2F45", "opacity": 1},
        "title": {
            "text": "Today’s Super Jackpot",
            "name": "RacingSansOne-Regular",
            "textsize": 60,
            "text_color": "#FFD000",
        },
        "line": {
            # "text": "01 05 08 10 11 16 17 18 20 56 78 90",  # 文字内容
            "name": "Inter_18pt-SemiBold",  # 字体
            "textsize": 30,  # 字号
            "text_color": "#ffffff",  # 文字颜色
            "padding_x": 10,  # 左右撑开 40px
            "padding_y": 10,  # 上下撑开 20px
            "stroke_width": 0,
            "bg_fill": "#6b29ce",  # 背景颜色（绿色）
            "bg_rx": 5,  # 大圆角
            "bg_stroke": "#ffffff",  # 白色边框
            "bg_stroke_width": 1,
            "bg_opacity": 0.45,
            "margin_bottom": 10,  # 下方留白
            "expand": True,
        },
        "spacing": {"height": 10},
        "text": {
            # "text": "Activity rules:\n1. Participate in the lottery\n2. Get rewards\n3. 祝您中的大奖\n4. 宝くじが当たりますように！",
            "name": "NotoSansSC-Regular",
            "textsize": 24,
            "align": "left",
            "stroke_width": 0,
            "text_color": RandColor(mode="neon"),
            "opacity": 1,
        },
        "circle": {
            "size": 45,
            "fill": "#FF0000",
            "text_color": "#FFFF00",
            "opacity": 0.9,
        },
    }
    renderer = Rendering(width=400 * 2, height=888 * 2, padding=30, level=10)
    exp_lines = [
        "03 07 21 23 29 33 + 03",
        "01 11 17 18 22 32 + 04",
        "15 18 20 26 31 32 + 02",
        "03 11 21 27 29 30 + 01",
        "04 07 17 23 24 26 + 04",
        "09 11 12 16 28 30 + 02",
        "03 05 15 19 29 33 + 03",
        "08 15 19 23 28 29 + 02",
        "20 21 22 28 29 33 + 02",
        "05 10 15 22 24 30 + 03",
        "03 05 10 13 20 24 + 04",
        "05 08 12 15 22 23 + 02",
        "01 03 09 18 30 32 + 02",
        "01 12 13 19 27 30 + 01",
        "04 07 12 16 25 32 + 04",
        "02 09 12 18 19 25 + 01",
        "07 13 21 23 25 29 + 03",
        "01 04 06 18 19 32 + 02",
        "04 05 08 14 18 20 + 02",
        "08 14 21 22 27 28 + 01",
    ]
    renderer.set_background(**style_conf["background"]).add_title(**style_conf["title"])
    # 渲染 文件头
    for index, line_text in enumerate(exp_lines, start=1):
        # 构建参数
        exp_conf = {
            "text": f"{index}: {line_text}",
            "text_color": RandColor(mode="neon"),
            "bg_fill": RandColor(mode="neon"),
        }
        line_conf = style_conf["line"]
        line_conf.update(exp_conf)
        renderer.add_text_with_bg(**line_conf)
        if index % 5 == 0 and index != len(exp_lines):
            renderer.add_spacing(**style_conf["spacing"])
            text_conf = style_conf["text"]
            info_conf = {
                "text": "God of Wealth Divider.",
                "text_color": RandColor(mode="neon"),
            }
            text_conf.update(info_conf)
            renderer.add_text(**text_conf)

    (
        renderer.add_text(
            text="☀ 动动手指, 把藏在云端的幸运领回家.\n☀ 财神爷正在敲门, 请准备好大大的口袋.\n☀ 选下你的心仪数字, 开启一份对生活的期待.",
            name="NotoSansSC-Regular",
            textsize=24,
            align="left",
            text_color=RandColor(mode="neon"),
        )
        .add_text(
            text="4. བསོད་ནམས་དཔལ་ཁ་དར་བར་ཤོག། བྱ་བ་ལམ་འགྲོ་ཡོང་བར་སྨོན།",
            name="Jomolhari-Regular",
            textsize=24,
            align="left",
            text_color=RandColor(mode="neon"),
        )
        .Write_to_file(filepath="./final_poster.png")
    )


if __name__ == "__main__":
    test_log_list()
