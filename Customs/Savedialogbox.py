# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-02 09:10:57
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-16 16:03:54


from .jackpot_core import randomData, filter_for_pabc
from .DraculaTheme import DraculaColors, RandColor, HarmonyColors
from .adbox import adbx
from .asyncredis import RedisAPI
from .svgbase64 import svgimage
from dataclasses import dataclass, field
from PIL import Image, ImageChops, ImageFont
from joblib import Parallel, delayed
import asyncio
import flet as ft
import datetime
import json
import io
import os
import sys
import time
import multiprocessing


# region _savedialog
class savedialog:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten, Child_padding=0)
        self.adb.setting_did_mount_callback(self.load_exp)
        self.exps_is_build = True
        self.getallexp = None

    def seting_get_all_exp(self, getallexp=None):
        self.getallexp = getallexp

    def __builde_conter(self):
        title_color = DraculaColors.ORANGE
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.genid = randomData.generate_secure_string(8)
        footer = ft.Row(
            controls=[
                ft.Text(
                    f"{now} {self.genid}",
                    size=14,
                    font_family="Inter_18pt-SemiBold",
                    color=ft.Colors.with_opacity(0.7, DraculaColors.ORANGE),
                )
            ],
            alignment=ft.MainAxisAlignment.END,
        )
        title = ft.Text(
            "Jackpot Lotter",
            size=28,
            weight="bold",
            font_family="RacingSansOne-Regular",
            color=title_color,
            italic=True,
        )

        self.exps = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=5,
        )
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.Button(
                    expand=2,
                    icon=ft.Icons.CANCEL,
                    bgcolor=ft.Colors.TRANSPARENT,
                    color=DraculaColors.FOREGROUND,
                    content="Cancel",
                    on_click=self.__handle_cancel,
                ),
                ft.Button(
                    expand=3,
                    icon=ft.Icons.IMAGE,
                    bgcolor=DraculaColors.RED,
                    color=DraculaColors.FOREGROUND,
                    content="Save to png",
                    on_click=self.__handle_save,
                ),
            ],
        )

        conter = ft.Container(
            width=float("inf"),
            padding=5,
            border_radius=10,
            bgcolor=DraculaColors.BACKGROUND,
            content=ft.Column(
                tight=True,
                spacing=5,
                controls=[
                    title,
                    self.exps,
                    footer,
                    acts,
                ],
            ),
        )
        self.Screenshot = ft.Screenshot(
            content=conter,
        )
        content = ft.Column(
            controls=[self.Screenshot],
            tight=True,
            on_size_change=self.handle_resize,
        )
        return content

    async def handle_resize(self, e):
        if e.height >= 772.0:
            await asyncio.sleep(1)
            self.adb.page.run_task(self.__handle_save)

    async def load_exp(self):
        self.exps_is_build = False
        if not self.getallexp:
            # print("not is getallexp func.")
            return
        all_exp = self.getallexp()
        if len(all_exp) == 0:
            # print("len all_exp is zero.")
            return
        items = []
        for i, _exp in enumerate(all_exp):
            items.append(self.CreateItem(_exp, i, 18))
            if (i + 1) % 5 == 0 and (i + 1) < len(_exp):
                items.append(self.CreateItem("", -1))
        self.exps.controls = items
        self.exps.update()
        self.exps_is_build = True

    def __handle_cancel(self):
        if self.adb.running:
            self.adb.page.pop_dialog()

    def CreateItem(self, text: str = "", i: int = 0, fontsize: int = 18):
        userColor = RandColor(mode="neon")
        twidth = 388 - 47
        if self.adb.page.platform.is_mobile():
            twidth = 292 - 47
        sizes = caclfsize(text=text, defsize=fontsize, targetwidth=twidth)
        # def onresize(e):
        #     print(f'onresize {e}')
        #     self.adb.page.show_dialog(ft.SnackBar(f"{e}"))
        # print(f'new font size {sizes}')
        item = (
            ft.Container(
                padding=5,
                width=float("inf"),  # 388
                bgcolor=ft.Colors.with_opacity(0.1, userColor),
                border_radius=5,
                # on_size_change=onresize,
                content=ft.Stack(
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    controls=[
                        ft.Text(
                            f"{text}",
                            size=sizes,
                            text_align=ft.TextAlign.START,
                            weight=ft.FontWeight.BOLD,
                            color=userColor,
                            font_family="Inter_18pt-SemiBold",
                        ),
                        ft.Image(
                            src=svgimage(i + 1),
                            width=fontsize * 1.68,
                            height=fontsize * 1.68,
                            color=ft.Colors.with_opacity(0.7, RandColor()),
                            right=-7,
                            bottom=-7,
                        ),
                    ],
                ),
            )
            if i >= 0
            else ft.Container(padding=5, height=10)
        )
        return item

    async def __handle_save(self):
        if self.exps_is_build:
            is_mobile_or_web = self.adb.page.web or self.adb.page.platform in [
                ft.PagePlatform.ANDROID,
                ft.PagePlatform.IOS,
            ]
            try:
                image = await self.Screenshot.capture()
                image = self.crop_solid_bg(image)
                png_name = f"{self.genid}.png"

                save_png = await ft.FilePicker().save_file(
                    file_type=ft.FilePickerFileType.CUSTOM,
                    allowed_extensions=["png"],
                    file_name=png_name,
                    src_bytes=image,
                )
                # print(f"save_path: {save_png}")
                if save_png and not is_mobile_or_web:
                    with open(save_png, "wb") as f:
                        f.write(image)
                        self.adb.page.show_dialog(
                            ft.SnackBar(f"{self.adb.page.platform} file save complete.")
                        )
                # print(f"Storage task completed.")
            except Exception as er:
                print(f"Image saving error. {er}")
            finally:
                await asyncio.sleep(1)
                self.adb.page.pop_dialog()

    def crop_solid_bg(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        # 2. 获取图片左上角 (0,0) 的像素颜色，假设这就是背景色
        # 如果你确定背景是白色，也可以直接写 bg_color = (255, 255, 255)
        bg_color = img.getpixel((img.width - 1, img.height - 1))
        # 3. 创建一张全背景色的假图片
        bg_img = Image.new("RGB", img.size, bg_color)
        # 4. 求差集，找到所有不是背景颜色的像素
        diff = ImageChops.difference(img, bg_img)
        # 5. 稍微模糊一下，处理边缘的抗锯齿毛边，并增强对比度
        diff = diff.convert("L").point(lambda x: 255 if x > 30 else 0)
        # 6. 获取所有非背景区域的边界
        bbox = diff.getbbox()
        if bbox:
            byte_stream = io.BytesIO()
            img.crop(bbox).save(byte_stream, format="PNG")
            # print(f"crop png -> {bbox}")
            return byte_stream.getvalue()
        return image_bytes


# endregion


# region _tadbx
@dataclass
class TaskState:
    result: list = field(default_factory=list)
    max_value: int = 100
    min_value: int = 0
    jdu: float = 0.0
    info: str = ""
    task: str = "none"

    async def addinfo(self, text: str) -> str:
        self.info = f"{text}"
        await asyncio.sleep(0.3)

    def getinfo(self) -> str:
        info = self.info
        self.info = None
        return info

    def additem(self, item):
        self.result.append(item)
        temp = [item[-1] for item in self.result]
        self.max_value = max(temp)
        self.min_value = min(temp)

    def getitems(self, sord: bool = False):
        if sord == False:
            return self.result[-10:]
        else:
            temp = list(sorted(self.result, key=lambda x: x[-1]))
            return temp


class tadbx:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten)
        self.detectstatus = TaskState()

    def __handle_Close(self, e):
        if self.adb.running and self.detectstatus.task == "none":
            self.adb.page.pop_dialog()

    def __handle_start(self, e):
        if self.adb.running and self.detectstatus.task == "none":
            self.detectstatus.task = "Detection"
            self.adb.page.run_task(self.Detection)
            self.adb.page.run_task(self.showresult)

    async def Detection(self):
        await self.detectstatus.addinfo("Load 'settings' and 'filters' data.")
        # await asyncio.sleep(0.3)
        settings = self.adb.page.session.store.get("settings")
        filtersAll = self.adb.page.session.store.get("filters")
        if not filtersAll:
            await self.detectstatus.addinfo("If filters is empty, skip the detection.")
            # await asyncio.sleep(0.3)
            self.detectstatus.task = "skip"
            return

        await self.detectstatus.addinfo("Create a data pool.")
        if settings and filtersAll:
            _rdpn = randomData(seting=settings["randomData"])
            results = []
            for i in range(1000):
                results.append(_rdpn.get_pabc())
        await asyncio.sleep(0.3)
        for i, _fitem in enumerate(filtersAll):
            # print(f"{_fitem}")
            _f2func = filter_for_pabc(filters=[_fitem])
            pass_rate = (
                sum([1 for r in results if _f2func.handle(r)]) / len(results) * 100
            )
            prinfo = [
                f"{_fitem['func']}",
                f"{_fitem['target']}",
                f"{_fitem['condition']}",
                int(pass_rate),
            ]
            self.detectstatus.jdu = (i + 1) / len(filtersAll)
            self.detectstatus.additem(prinfo)
            await self.detectstatus.addinfo(
                f"{_fitem['func']} {_fitem['target']} {_fitem['condition']}"
            )
            if pass_rate < 1.0:
                self.detectstatus.task = "pass_rate_zero"
                return

        self.detectstatus.task = "none"

    async def showresult(self):
        while self.detectstatus.task in ["Detection", "pass_rate_zero", "skip"]:
            await asyncio.sleep(0.3)
            text = self.detectstatus.getinfo()
            if text:
                self.info_display.controls[0].value = text
            self.smax.content.value = self.detectstatus.max_value
            self.smin.content.value = self.detectstatus.min_value
            self.pbar.value = self.detectstatus.jdu
            self.tips.value = (
                f"Testing in progress... {self.pbar.value * 100:.0f}% complete"
            )
            self.adb.content.update()
            if self.detectstatus.task in ["pass_rate_zero", "skip"]:
                self.detectstatus.task = "none"
                return

        self.info_display.controls[0].value = "Test complete ✔"
        self.info_display.controls[0].update()

    def __builde_conter(self):
        title = ft.Row(
            spacing=3,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.SETTINGS_ACCESSIBILITY, size=18),
                ft.Text(
                    "Filter Testing Dashboard",
                    size=18,
                    weight="bold",
                    color=DraculaColors.FOREGROUND,
                ),
            ],
        )
        maxmin = ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                _smax := ft.Container(
                    expand=1,
                    height=65,
                    # 1. 删除 padding=10，避免上下空间被挤压
                    # 2. 加上 alignment，让内部文字完美水平+垂直居中
                    alignment=ft.Alignment.CENTER,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(
                        0.1, RandColor(mode="neon", hue="green")
                    ),
                    border=ft.Border.all(
                        1,
                        ft.Colors.with_opacity(
                            0.2, RandColor(mode="neon", hue="green")
                        ),
                    ),
                    content=ft.Text(
                        "78",
                        size=40,
                        color=ft.Colors.with_opacity(
                            0.8, RandColor(mode="neon", hue="green")
                        ),
                        # text_align="center" # 其实加了 alignment 后，这个可以不写了
                    ),
                ),
                _smin := ft.Container(
                    expand=1,
                    height=65,
                    alignment=ft.Alignment.CENTER,  # 同上，完美居中
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(
                        0.1, RandColor(mode="neon", hue="red")
                    ),
                    border=ft.Border.all(
                        1,
                        ft.Colors.with_opacity(0.2, RandColor(mode="neon", hue="red")),
                    ),
                    content=ft.Text(
                        "23",
                        size=40,
                        color=ft.Colors.with_opacity(
                            0.8, RandColor(mode="neon", hue="red")
                        ),
                    ),
                ),
            ],
        )
        self.smax = _smax
        self.smin = _smin
        schedule = ft.Column(
            tight=True,
            spacing=5,
            controls=[
                tips := ft.Text(
                    "Testing in progress...84% complete",
                    size=15,
                    weight="bold",
                    color=RandColor(mode="neon", hue="blue"),
                    text_align=ft.TextAlign.END,
                ),
                pbar := ft.ProgressBar(
                    value=0.5,
                    expand=1,
                    height=10,
                    color=RandColor(mode="neon"),
                    border_radius=5,
                ),
            ],
        )
        self.tips = tips
        self.pbar = pbar
        self.info_display = ft.Column(
            tight=True,
            spacing=3,
            scroll=ft.ScrollMode.HIDDEN,
            controls=[
                ft.Text(
                    "Click the `Start testing` to begin the test.",
                    italic=True,
                    color=ft.Colors.with_opacity(0.7, "#bebebe"),
                ),
            ],
        )
        # def handle_more_on_siee(e):
        #     print(f"more e: {e}")
        self.more_display = ft.Column(
            data="hide",  # hide or show
            tight=True,
            spacing=0,
            scroll=ft.ScrollMode.HIDDEN,
            controls=[self.Details(type="more")],
            # on_size_change=handle_more_on_siee
        )
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.TextButton(
                    "Close",
                    expand=1,
                    on_click=self.__handle_Close,
                    style=ft.ButtonStyle(color="#dfdfdf"),
                ),
                # 确定按钮用红色突出显示危险操作
                ft.Button(
                    "Start testing",
                    expand=3,
                    color=DraculaColors.FOREGROUND,
                    bgcolor=DraculaColors.RED,
                    on_click=self.__handle_start,
                ),
            ],
        )
        conter = ft.Container(
            # width=400,
            padding=5,
            border_radius=0,
            content=ft.Column(
                tight=True,
                spacing=5,
                controls=[
                    title,
                    maxmin,
                    schedule,
                    self.more_display,
                    self.info_display,
                    acts,
                ],
            ),
        )
        return conter

    async def handle_more(self, e):
        items = self.detectstatus.getitems(sord=True)
        if not items:
            return
        if self.more_display.data == "hide":
            self.more_display.data = "show"
            self.more_display.height = 160
        elif self.more_display.data == "show":
            self.more_display.data = "hide"
            self.more_display.height = 20
        if self.more_display.controls.__len__() == 1:
            for item in items:
                self.more_display.controls.append(self.Details(*item, type="info"))
        self.more_display.update()

    def Details(self, *args, **kwargs):
        bold = kwargs.get("bold", False)
        size = kwargs.get("size", 14)
        typed = kwargs.get("type", "more")  # more info
        usercolor = kwargs.get("usercolor", RandColor(mode="neon"))
        match typed:
            case "more":
                temp = ft.Container(
                    padding=0,
                    content=ft.Row(
                        spacing=5,
                        controls=[
                            ft.Container(
                                padding=0,
                                expand=True,
                                height=1,
                                bgcolor=DraculaColors.FOREGROUND,
                            ),
                            ft.Container(
                                padding=0,
                                content=ft.Text("* MORE *"),
                                on_click=self.handle_more,
                            ),
                        ],
                    ),
                )
            case "info":
                f, t, c, pr = args
                pr = f"{pr}%"
                # print(f'{args}')
                temp = ft.Container(
                    padding=2,
                    content=ft.Row(
                        spacing=3,
                        controls=[
                            ft.Text(
                                f"{pr:<5}", weight="bold", color=RandColor(hue="red")
                            ),
                            ft.Text(f"{f}", color=RandColor(hue="blue")),
                            ft.Text(
                                f"{t:<2}", weight="bold", color=RandColor(hue="yellow")
                            ),
                            ft.Text(f"{c}", color=RandColor(hue="green")),
                        ],
                    ),
                )
            case _:
                pass
        return temp


# endregion


# region upstash token


class upstashtoken:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten)
        self.detectstatus = TaskState()
        self.valid_data = None

    def __builde_conter(self):
        title = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Configuration", size=18, color=DraculaColors.FOREGROUND),
                ft.Text(
                    "Adjust your preferences below",
                    size=13,
                    color=ft.Colors.with_opacity(0.4, DraculaColors.FOREGROUND),
                ),
            ],
        )
        # 显示token 输入窗口
        apitoken = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text(
                    "API Token".upper(),
                    size=13,
                    color=ft.Colors.with_opacity(0.4, DraculaColors.FOREGROUND),
                ),
                intoken := ft.TextField(
                    hint_text="Enter your token",
                    border=ft.InputBorder.NONE,
                    cursor_height=15,
                    text_size=15,
                    dense=True,
                    content_padding=ft.Padding.all(0),
                ),
                intoken_url := ft.TextField(
                    hint_text="https://******.upstash.io",
                    border=ft.InputBorder.NONE,
                    cursor_height=15,
                    text_size=15,
                    dense=True,
                    content_padding=ft.Padding.all(0),
                ),
                intoken_tip := ft.Text(
                    "Securely sync your project data using your unique access key.",
                    no_wrap=False,
                    max_lines=2,
                    size=12,
                    color=ft.Colors.with_opacity(0.4, DraculaColors.FOREGROUND),
                ),
            ],
        )
        self.intoken = intoken
        self.intoken_tip = intoken_tip
        self.intoken_url = intoken_url
        asyncset = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Text(
                    "Settings".upper(),
                    size=13,
                    color=ft.Colors.with_opacity(0.4, DraculaColors.FOREGROUND),
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Sync Data",
                            size=15,
                            color=ft.Colors.with_opacity(1, DraculaColors.FOREGROUND),
                        ),
                        switch := CustomSwitch(value=False),
                    ]
                ),
            ],
        )
        self.syncsw = switch
        # 取消 按钮牛
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.handle_cancel,
                    style=ft.ButtonStyle(
                        color=ft.Colors.with_opacity(0.8, DraculaColors.FOREGROUND)
                    ),
                ),
                # 确定按钮用红色突出显示危险操作
                ft.TextButton(
                    "Apply",
                    on_click=self.handle_apply,
                    style=ft.ButtonStyle(color=RandColor(hue="blue")),
                ),
            ],
        )
        conter = ft.Container(
            # width=400,
            padding=5,
            border_radius=0,
            content=ft.Column(
                tight=True,
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    title,
                    apitoken,
                    ft.Divider(color=DraculaColors.FOREGROUND),
                    asyncset,
                    acts,
                ],
            ),
        )
        return conter

    def setting_apply_callback(self, callblack):
        self.applycallback = callblack

    def setting_valid_info(self, jsondata):
        while isinstance(jsondata, str):
            jsondata = json.loads(jsondata)
        self.intoken.value = jsondata["token"]
        self.intoken_url.value = jsondata["url"]
        self.syncsw.value = jsondata["sync"]
        self.valid_data = jsondata
        self.adb.update()

    def handle_cancel(self):
        self.adb.page.pop_dialog()

    async def handle_apply(self):
        # 1. 提取 UI 更新辅助函数，消除重复的冗余代码
        async def show_tip(msg: str, color: str):
            self.intoken_tip.value = msg
            self.intoken_tip.color = ft.Colors.with_opacity(1, color)
            self.intoken_tip.update()  # 先更新 UI 给用户看
            await asyncio.sleep(0.5)  # 再稍微停留一下

        # 获取并清理输入（去除首尾空格）
        token = self.intoken.value.strip()
        token_url = self.intoken_url.value.strip()

        # 2. 基础输入校验
        if not token:
            await show_tip("Please enter the upstash token.", DraculaColors.RED)
            return

        if not token_url:
            await show_tip(
                "Please enter upstash to retrieve the URL.", DraculaColors.RED
            )
            return

        # 修复 Bug：正确补全 HTTPS
        if not token_url.startswith(("http://", "https://")):
            token_url = f"https://{token_url}"

        # 3. 缓存检测（如果信息没变且之前验证过，直接生效并退出）
        # 使用 dict.get 更加安全，防止 KeyError
        if (
            self.valid_data
            and self.valid_data.get("valid")
            and self.valid_data.get("token") == token
            and self.valid_data.get("url") == token_url
        ):
            self.valid_data["sync"] = self.syncsw.value
            if self.applycallback:
                self.adb.page.run_task(self.applycallback, self.valid_data)
            self.adb.page.pop_dialog()
            return

        # 4. 开始 API 测试流程
        await show_tip("Connecting to Upstash...", DraculaColors.YELLOW)

        redisapi = RedisAPI(url=token_url, token=token)
        test_token = "abc_123_xyz"
        user_id = "user_999"

        try:
            # 第一步：尝试写入数据
            save_success = await redisapi.save_token(
                test_token, user_id, expire_seconds=30
            )
            if not save_success:
                await show_tip("Connection failed. Check URL/Token.", DraculaColors.RED)
                return

            # 第二步：尝试读取数据并验证
            await show_tip("Verifying saved data...", DraculaColors.GREEN)
            result = await redisapi.verify_token(test_token)

            # 5. 最终结果处理
            if result.get("is_valid"):
                # 验证成功
                await show_tip("Token verified successfully!", DraculaColors.GREEN)

                if self.applycallback:
                    backdata = {
                        "token": token,
                        "url": token_url,
                        "valid": True,
                        "sync": self.syncsw.value,
                    }
                    self.adb.page.run_task(self.applycallback, backdata)

                self.adb.page.pop_dialog()
                return  # 修复 Bug：验证成功后必须 return，防止穿透到下面

            else:
                # 验证失败
                await show_tip("Token verification failed.", DraculaColors.RED)

        except Exception as e:
            # 捕获网络异常等未预期错误
            await show_tip(f"Error: {str(e)[:20]}", DraculaColors.RED)


# endregion


# region Custom_Switch
class CustomSwitch(ft.Container):
    def __init__(self, value: bool = False, on_change=None):
        super().__init__()
        self._load_colors()

        # --- 容器基础属性 ---
        self.width = 35
        self.height = 20
        self.padding = 3
        self.border_radius = self.height / 2
        self.border = ft.Border.all(1, self.border_color)
        # 修正：使用 Flet 标准动画枚举
        self.animate = ft.Animation(400, ft.AnimationCurve.DECELERATE)
        self.on_click = self._toggle_switch

        # --- 状态与回调 ---
        self._value = value
        self.on_change = on_change

        # --- 构建内部滑块 ---
        self.content = self._build_handle()

        # --- 强制同步初始 UI 与初始状态 ---
        self._update_ui_state(self._value)

    # 💡 优化 1：使用 property，可以用 switch.value = True 直接赋值
    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, new_value: bool):
        self._value = new_value
        self._update_ui_state(new_value)
        # 💡 优化 2：安全更新，防止在 Mount 前调用导致报错
        if self.page:
            self.update()

    def setingbadge(self, value: int):
        if value == None or value == -1:
            self.badge = None
        else:
            self.badge = f"{value}"
        if self.page:
            self.update()

    def _update_ui_state(self, is_active: bool):
        """内部方法：根据当前布尔值更新 UI 样式"""
        # ⚠️ 注意：这里保留了你原本的逻辑 (True在左侧，False在右侧)
        # 如果你想改成常规的 (True在右边开启)，请把下面 True 和 False 的代码互换
        if is_active:
            self.bgcolor = ft.Colors.with_opacity(0.3, self.active_color)
            self.alignment = ft.Alignment.CENTER_RIGHT
            self.handle.bgcolor = self.default_color
        else:
            self.bgcolor = ft.Colors.with_opacity(0.3, self.default_color)
            self.alignment = ft.Alignment.CENTER_LEFT
            self.handle.bgcolor = self.active_color

    def _load_colors(self):
        """加载颜色 (修复了拼写)"""
        self.active_color = RandColor(hue="red")
        self.default_color, self.border_color = HarmonyColors(
            base_hex_color=self.active_color, harmony_type="triadic"
        )

    def _build_handle(self):
        self.handle = ft.Container(
            height=12,
            width=12,
            border_radius=6,
            bgcolor=self.active_color,
            border=ft.Border.all(1, self.border_color),
            # 💡 优化 3：给内部滑块也加上动画，颜色过渡会非常柔和
            animate=ft.Animation(400, ft.AnimationCurve.DECELERATE),
        )
        return self.handle

    def _toggle_switch(self, e):
        # 切换状态，自动触发 @value.setter 里的 UI 更新逻辑
        self.value = not self.value

        # 触发外部传入的回调函数
        if self.on_change:
            self.on_change(self)


# endregion


# region CasfontW
def caclfsize(
    text: str,
    fontname: str = None,
    targetwidth: int = 355,
    defsize: int = 18,
    maxsize: int = 26,
) -> int:
    """
    根据目标像素宽度计算最佳字体大小
    :param fontpath: .ttf 字体文件的物理路径
    :param text: 要显示的文本内容
    :param targetwidth: 目标的像素宽度 (默认 360)
    :param defsize: 默认大小、起始大小
    :param maxsize: 最大值
    :return: 建议的 font_size (int)
    """
    low = 1
    high = maxsize  # 设置一个合理的上限
    best_size = defsize

    if not fontname:
        fontname = "Inter_18pt-SemiBold"

    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # 向上跳一级到 /src/，再进入 assets/fonts/
    FONT_PHYSICAL_PATH = os.path.abspath(
        os.path.join(CURRENT_DIR, "..", "assets", "fonts", f"{fontname}.ttf")
    )

    # 使用二分法快速逼近目标宽度
    while low <= high:
        mid = (low + high) // 2
        try:
            font = ImageFont.truetype(FONT_PHYSICAL_PATH, mid)
            # 获取文本渲染后的边界框 [left, top, right, bottom]
            bbox = font.getbbox(text)
            current_width = bbox[2] - bbox[0]

            if current_width <= targetwidth:
                best_size = mid
                low = mid + 1
            else:
                high = mid - 1
        except Exception as ex:
            # print(f'caclfsize error, use defsize {defsize}: {ex}')
            return defsize
    return max(defsize, best_size)


# ednregion


# region joblibdlg
class joblibdlg:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten)
        self.taskbar_value = 0
        self.is_computing = False
        self.valid_results = []

    def handle_cancel(self):
        if self.is_computing:
            return
        self.adb.page.pop_dialog()

    def setting_add_remove(self, add=None, remove=None):
        self.additem = add
        self.removeitem = remove

    async def handle_start(self):
        if self.is_computing:
            return
        settings = self.adb.page.session.store.get("settings")
        filters = self.adb.page.session.store.get("filters")
        timeout_limit = 60
        target_quantity = 0  # 设为 0 则在 60秒内尽可能多地计算
        max_time = 5
        self.valid_results = []
        try:
            if self.intimeout.value != "":
                timeout_limit = int(self.intimeout.value)
            if self.intargetquantity.value != "":
                target_quantity = int(self.intargetquantity.value)
            if timeout_limit == 0 and target_quantity == 0:
                timeout_limit = 60
            if self.inmaxtime.value != "":
                max_time = int(self.inmaxtime.value)
                max_time = max_time if max_time < 60 else 60
            if timeout_limit == 0 and target_quantity >= 1:
                timeout_limit = 60 * max_time
        except Exception as ex:
            print(f"seting erro, use default value. {ex}")

        self.adb.page.run_task(self.InspectProgress)
        temp = await asyncio.to_thread(
            self.run_parallel, settings, filters, timeout_limit, target_quantity
        )
        print(f"{temp=}")

    async def InspectProgress(self):
        await asyncio.sleep(0.5)
        _last_value = -1
        _last_count = 0
        while self.is_computing:
            await asyncio.sleep(1)
            if _last_value == self.taskbar_value:
                continue
            self.showbar.value = f"Task {self.taskbar_value * 100:.0f}% Complete"
            self.taskbar.value = self.taskbar_value
            self.taskbar.update()
            self.showbar.update()
            _last_value = self.taskbar_value
            current_count = len(self.valid_results)
            if current_count > _last_count:
                # 利用切片获取自上次检查以来新增的所有数据
                new_items = self.valid_results[_last_count:current_count]
                # 遍历打印出新发现的数据
                for item in new_items:
                    print(f"🎉 发现新数据: {item}")
                    if self.additem and self.removeitem:
                        self.additem(self.removeitem, item)

                # 更新计数器
                _last_count = current_count
        await asyncio.sleep(1)
        self.showbar.value = (
            f"Core-Link Parallelizer found {self.valid_results.__len__()} items."
        )
        print(f"Core-Link Parallelizer found {self.valid_results.__len__()} items.")
        self.showbar.update()

    def run_parallel(self, settings, filters, timeout_limit, target_quantity):
        self.is_computing = True
        self.taskbar_value = 0
        final_results = self.run_parallel_calculations(
            settings=settings,
            filters=filters,
            timeout=timeout_limit,
            Quantity=target_quantity,
        )
        self.taskbar_value = 1
        self.is_computing = False
        return final_results

    def __builde_conter(self):
        title = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "Core-Link Parallelizer", size=18, color=DraculaColors.FOREGROUND
                ),
                ft.Text(
                    "Scaling heavy computations through seamless Joblib-driven parallelization.",
                    size=14,
                    color=ft.Colors.with_opacity(0.4, DraculaColors.FOREGROUND),
                ),
            ],
        )
        jobsetting = ft.Column(
            tight=True,
            width=float("inf"),
            spacing=0,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Row(
                    controls=[
                        ft.Text(
                            "timeout limit:",
                            size=15,
                            color=ft.Colors.with_opacity(1, DraculaColors.FOREGROUND),
                        ),
                        in_timeout := ft.TextField(
                            hint_text="60 seconds",
                            border=ft.InputBorder.NONE,
                            cursor_height=15,
                            text_size=15,
                            dense=True,
                            content_padding=ft.Padding.all(0),
                        ),
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "target quantity:",
                            size=15,
                            color=ft.Colors.with_opacity(1, DraculaColors.FOREGROUND),
                        ),
                        in_target_quantity := ft.TextField(
                            hint_text="0 quantity",
                            border=ft.InputBorder.NONE,
                            cursor_height=15,
                            text_size=15,
                            dense=True,
                            content_padding=ft.Padding.all(0),
                        ),
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "Maximum Calculation Time:",
                            size=15,
                            color=ft.Colors.with_opacity(1, DraculaColors.FOREGROUND),
                        ),
                        in_max_time := ft.TextField(
                            hint_text="5 minutes",
                            border=ft.InputBorder.NONE,
                            cursor_height=15,
                            text_size=15,
                            dense=True,
                            content_padding=ft.Padding.all(0),
                        ),
                    ]
                ),
                ft.Row(height=5),
                ft.Row(
                    controls=[
                        showbar := ft.Text(
                            "The task has not yet started.",
                            size=15,
                            italic=True,
                            color=RandColor(mode="neon"),
                        ),
                    ]
                ),
                ft.Row(
                    controls=[
                        tbar := ft.ProgressBar(
                            value=0.5,
                            expand=1,
                            height=10,
                            color=RandColor(mode="neon"),
                            border_radius=5,
                        ),
                    ],
                ),
            ],
        )
        self.intimeout = in_timeout
        self.intargetquantity = in_target_quantity
        self.inmaxtime = in_max_time
        self.taskbar = tbar
        self.showbar = showbar
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.handle_cancel,
                    style=ft.ButtonStyle(
                        color=ft.Colors.with_opacity(0.8, DraculaColors.FOREGROUND)
                    ),
                ),
                # 确定按钮用红色突出显示危险操作
                ft.TextButton(
                    "Start",
                    on_click=self.handle_start,
                    style=ft.ButtonStyle(color=RandColor(hue="blue")),
                ),
            ],
        )
        conter = ft.Container(
            # width=400,
            padding=5,
            border_radius=0,
            content=ft.Column(
                tight=True,
                spacing=8,
                alignment=ft.MainAxisAlignment.START,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    title,
                    jobsetting,
                    ft.Divider(color=DraculaColors.FOREGROUND),
                    acts,
                ],
            ),
        )
        return conter

    def run_parallel_calculations(self, settings, filters, timeout=60, Quantity=0):
        """
        使用 joblib 执行多进程计算

        :param settings: dict, 必填，计算设置
        :param filters: dict, 必填，过滤校验规则
        :param timeout: int, 运行时长(秒)，默认 60 为0 则不限制执行时间
        :param Quantity: int, 需要的正确结果数量，默认 10。如果为 0 则不限制数量。
        :return: list, 满足条件的计算结果列表
        """
        if not settings or not filters:
            return self.valid_results
        os.environ["PYTHONPATH"] = os.pathsep.join(sys.path)
        start_time = time.time()

        # 获取 CPU 核心数，决定进程数
        n_cores = multiprocessing.cpu_count()

        # 动态调整批处理大小(Batch Size)
        # 如果限制了 Quantity，批次小一点，防止过度计算浪费算力
        # 如果 Quantity == 0，批次大一点，减少 joblib 分发任务的通信开销
        batch_size = n_cores * 2 if Quantity > 0 else n_cores * 10

        # 启动进程池 (n_jobs=-1 表示使用所有可用 CPU 核心)
        # backend="loky" 是 joblib 默认且最适合 CPU 密集型任务的后端
        with Parallel(n_jobs=-1, backend="loky") as parallel:
            while True:
                # 1. 超时检查：如果超过预设时间，立即停止并返回
                if time.time() - start_time >= timeout:
                    break

                # 2. 提交一批任务给多进程执行
                # 这里使用了生成器表达式，延迟计算
                batch_tasks = (
                    delayed(calculate_lottery)(settings, filters)
                    for _ in range(batch_size)
                )

                # 收集当前批次的结果
                batch_results = parallel(batch_tasks)

                # 3. 解析当前批次的结果
                for exp_result, is_valid in batch_results:
                    if is_valid:
                        self.valid_results.append(exp_result)

                    # 4. 数量检查：如果在批次解析中途达到了 Quantity 限制，立即返回
                    if Quantity > 0 and len(self.valid_results) >= Quantity:
                        # 返回精确数量的结果（截取掉可能多算出来的部分）
                        return self.valid_results[:Quantity]

                    # 即使在解析结果时，也顺便检查一下是否超时
                    if time.time() - start_time >= timeout:
                        return self.valid_results
                if Quantity == 0:
                    self.taskbar_value = (time.time() - start_time) / timeout
                else:
                    self.taskbar_value = self.valid_results.__len__() / Quantity

        # 循环结束（通常是因为触发了 timeout）
        return self.valid_results


def calculate_lottery(settings, filters):
    """
    纯函数，用于单次彩票计算。
    移除了对 self.page 的依赖，直接通过参数获取 settings 和 filters
    """
    if not settings:
        return ("No settings", False)

    # 实例化并获取数据
    rd = randomData(seting=settings["randomData"])
    result = rd.get_pabc()

    # 如果没有过滤器，直接返回 True
    if not filters:
        return (rd.get_exp(result), True)

    # 过滤校验
    filter_jp = filter_for_pabc(filters=filters)
    if filter_jp.handle(result) == False:
        return (rd.get_exp(result), False)

    return (rd.get_exp(result), True)


# endregion
