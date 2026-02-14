# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-14 02:14:29

from .jackpot_core import randomData, filter_for_pabc
from .SnackBar import get_snack_bar
from .DraculaTheme import DraculaColors
from .loger import logr
import flet as ft
import datetime
import os
import asyncio
import time
import re

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


# region serendipitousCapture
class serendipitousCapture(ft.Card):
    """创建一个控件 用来使用列表拍照"""

    def __init__(self):
        super().__init__()
        self.get_exp_all = None
        self.scshot = self.__build_exp()
        self.tips = self.__build_tips()
        self.content = self.__build__Container()
        self.visible = False
        # self.width = 400

    def setting_get_exp_all(self, getexpall: list = None):
        self.get_exp_all = getexpall

    def did_mount(self):
        self.running = True
        # self.setting_width()

    def will_unmount(self):
        self.running = False

    async def update_tips(self, text: str = ""):
        self.tips.value = f"{text}"
        self.tips.update()
        await asyncio.sleep(1)

    async def espcap_windows(self):
        for i in range(1, 4):
            await self.update_tips(f"The window will close in {3 - i} seconds.")

    # region add_exp
    async def add_exp(self, exp: list = None, genid: str = None):
        if not exp or not genid:
            return

        def eTotext(text: str = "", i=0):
            if text not in ["", None]:
                text = f"{chr(65 + i)}: {_e}"
                color = "#E70224" if i % 2 == 0 else "#d7a700"
                size = 18
                weight = ft.FontWeight.BOLD
                font_family = "RacingSansOne-Regular"
            else:
                text = "Billionaire!"
                color = ft.Colors.with_opacity(0.3, "#FFFFFF")
                size = 12
                weight = ft.FontWeight.W_100
                font_family = None
            return ft.Text(
                value=text,
                size=size,
                color=color,
                weight=weight,
                font_family=font_family,
            )

        esc = [x for x in self.showNumbers.controls if x.data == "biaoyu"]
        cols = []
        for i, _e in enumerate(exp):
            #! _e is row
            cols.append(eTotext(_e, i))
            if (i + 1) % 5 == 0 and (i + 1) < len(exp):
                cols.append(eTotext("", i))
        esc.append(
            ft.Container(
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=cols,
                ),
                # 【关键】用 Container 的底边框代替 Divider
                border=ft.border.only(
                    bottom=ft.BorderSide(2, "#7b0000"), top=ft.BorderSide(2, "#7b0000")
                ),
                padding=ft.padding.only(bottom=10, top=10, left=5, right=5),
            )
        )
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        esc.append(
            ft.Text(
                value=f"{now} {genid}",
                size=12,
                color="#7b0000",
            )
        )
        self.showNumbers.controls = esc
        self.showNumbers.update()

    # endregion

    # region schot_exp_capture
    async def schot_exp_capture(self):
        """外部函数调用 并执行截图"""
        try:
            self.visible = True
            self.update()
            if not self.running:
                await self.update_tips("running is not.")
                return
            if not self.get_exp_all:
                await self.update_tips("No data to capture.")
                return
            exp_all = self.get_exp_all()
            if not exp_all:
                await self.update_tips("No data was obtained.")
                return
            await self.update_tips(f"Retrieve {len(exp_all)} data entries.")
            genid = randomData.generate_secure_string(8)
            await self.add_exp(exp_all, genid)

            is_mobile_or_web = self.page.web or self.page.platform in [
                ft.PagePlatform.ANDROID,
                ft.PagePlatform.IOS,
            ]

            image = await self.scshot.capture()
            png_name = f"{genid}.png"
            logr.info(f"{image.__sizeof__()=} {png_name=}")

            save_png = await ft.FilePicker().save_file(
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["png"],
                file_name=png_name,
                src_bytes=image,
            )
            logr.info(f"save_path: {save_png}")
            if save_png and not is_mobile_or_web:
                with open(save_png, "wb") as f:
                    f.write(image)
                await self.update_tips(f"Storage file directory {png_name}.")
            await self.update_tips(f"Storage task completed.")

        except Exception as er:
            logr.info(f"Capture error. {er}")
        finally:
            self.visible = False
            await self.espcap_windows()
            self.update()

    # endregion

    def __build_tips(self):
        return ft.Text("save to ...", size=16, color=DraculaColors.ORANGE)

    def __build_exp(self):
        self.showNumbers = ft.Column(
            tight=True,
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            # horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Text(
                    "Jackpot Lotter",
                    size=25,
                    weight="bold",
                    font_family="RacingSansOne-Regular",
                    color="#7b0000",
                    italic=True,
                    data="biaoyu",
                ),
            ],
        )
        return ft.Screenshot(
            content=ft.Container(
                foreground_decoration=ft.BoxDecoration(
                    # bgcolor=DraculaColors.CURRENT_LINE,
                    image=ft.DecorationImage(
                        src="fa.png",
                        fit=ft.BoxFit.NONE,
                        # repeat=ft.ImageRepeat.REPEAT,
                        opacity=0.1,
                    ),
                ),
                bgcolor="#1f1f1f",
                border_radius=5,
                padding=10,
                content=self.showNumbers,
            )
        )

    def __build__Container(self):
        # 注意：这里 self.exp_list 已经是字符串或列表，逻辑保持你的不变
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=600,
            border=ft.Border.all(1, DraculaColors.ORANGE),
            border_radius=10,
            content=ft.Column(
                controls=[
                    self.scshot,
                    ft.Divider(),
                    self.tips,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
        )


# endregion


# region itemC2plus
class itemC2plus(ft.Container):
    def __init__(self):
        super().__init__()
        self.timeout = 30
        self.threshold = 120
        self.is_refreshing = False
        self.running = False
        self.state_exp = "none"  # "ref" "done"
        self.Itemc2_remove = None
        self.fontSize = 25
        self.selected = False
        # 参数

        self.padding = 15
        self.border_radius = 10
        self.bgcolor = DraculaColors.CRADBG
        self.content = self.__build_content()

    def __build_tips(self):
        self.tips = ft.Text(
            value="Please wait...",
            no_wrap=True,
            size=13,
            color=ft.Colors.with_opacity(0.5, DraculaColors.FOREGROUND),
        )

        def handle_animation_end(e):
            if conta.offset == ft.Offset(0, 0):
                conta.offset = ft.Offset(-0.5, 0)  # 向左移动自身宽度的 50%
            else:
                conta.offset = ft.Offset(0, 0)
            conta.update()
            # end

        conta = ft.Container(
            content=self.tips,
            width=200,
            alignment=ft.Alignment.CENTER_RIGHT,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            border=ft.Border.only(
                left=ft.BorderSide(5, ft.Colors.RED)  # 宽度为5的红色左边框
            ),
            padding=ft.Padding.only(left=5),
            # 动画配置
            animate_offset=ft.Animation(3000, ft.AnimationCurve.EASE_IN_OUT),
            on_animation_end=handle_animation_end,
            offset=ft.Offset(0, 0),
        )
        return conta

    def tips_value(self, value: str, color: str = DraculaColors.FOREGROUND):
        self.tips.value = f"{value}"
        self.tips.color = ft.Colors.with_opacity(0.5, color)
        self.tips.tooltip = ft.Tooltip(message=f"{value}")
        # self.tips.update()

    def displayNumbers(self, text: str, size: int = 35):
        """用环形标示 标识出数字"""
        result = re.findall(r"\d+|\+", text)
        row = ft.Row(
            wrap=False,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            spacing=5,
        )
        colors = [["#d9dbdf", "#747fdf"], ["#eab425", "#fbbf24"]]
        quan, shuzi = colors[0]
        for key in result:
            if key == "+":
                quan, shuzi = colors[1]
                continue
            item = ft.Container(
                content=ft.Text(
                    value=f"{key}",
                    size=size * 0.5,  # 字体大小约为容器的一半
                    weight=ft.FontWeight.BOLD,
                    color=shuzi,  # 文字建议也用金色系或对比色
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=ft.Colors.TRANSPARENT,  # 背景透明
                border=ft.Border.all(1, quan),
                width=size,
                height=size,
                border_radius=size / 2,
                padding=ft.Padding.all(5),
            )
            row.controls.append(item)
        return row

    def did_mount(self):
        if not self.running and not self.is_refreshing and self.state_exp != "done":
            self.refresh(name="did_mount")

    def will_unmount(self):
        self.running = False

    def __build__badge(self, size: int = 20, text: str = "111"):
        self.buildBadge = ft.Container(
            content=ft.Text(
                f"{text}",
                size=size * 0.5,
                weight="bold",
                color=DraculaColors.FOREGROUND,
                text_align=ft.TextAlign.CENTER,
            ),
            padding=ft.Padding(8, 5, 8, 5),
            # width=size,
            # height=size,
            bgcolor=DraculaColors.RED,
            border_radius=size / 2,  # 半径设为宽高的一半即为正圆
            # alignment=ft.Alignment.CENTER,  # 确保图标在内部居中
        )
        return self.buildBadge

    def __build_check(self, size: int = 30):
        def toggle_icon(e):
            # 切换选中状态
            if self.state_exp != "done":
                return
            # e.control.selected = not e.control.selected
            # e.control.update()
            self.selected = not self.selected
            self.check.bgcolor = DraculaColors.GREEN if self.selected else None
            self.check.update()
            logr.info(f"{self.selected}")
            # end

        self.check = ft.Container(
            padding=5,
            content=ft.Icon(
                ft.Icons.CHECK, color=DraculaColors.FOREGROUND, size=size * 0.6
            ),
            width=size,
            height=size,
            border_radius=size / 2,
            alignment=ft.Alignment.CENTER,
            on_click=toggle_icon,
        )
        return self.check

    def __build_Butter(self, size=30, icon=ft.Icons.REFRESH, onclick=None):
        butter = ft.Container(
            # padding=5,
            content=ft.Icon(icon, color=DraculaColors.FOREGROUND, size=size),
            # width=size,
            # height=size,
            # border_radius=size / 2,
            # alignment=ft.Alignment.CENTER,
            on_click=onclick if onclick else None,
        )
        return butter

    def __build_content(self):
        content = ft.Column(
            spacing=0,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    expand=1,
                    controls=[
                        shownumber := self.displayNumbers("05 06 07"),
                        self.__build_check(),
                    ],
                ),
                ft.Row(
                    expand=1,
                    spacing=5,
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        self.__build_tips(),
                        self.__build_Butter(
                            30, ft.Icons.REFRESH, self.handle_refresh_data
                        ),
                        self.__build_Butter(
                            30, ft.Icons.DELETE_FOREVER, self.handle_delete
                        ),
                        self.__build__badge(text="0"),
                    ],
                ),
            ],
        )
        self.showNumber = shownumber
        return content

    def setting_Itemc2_Remove(self, itemc2remove=None):
        self.Itemc2_remove = itemc2remove

    def refresh(self, name: str = "None"):
        if self.is_refreshing or self.selected:
            return
        # logr.info(f"markdata is running. {name}")
        self.page.run_task(self.SearchForData, name)

    # region SearchForData
    async def SearchForData(self, name: str):
        logr.info(f"SearchForData {name}")
        self.is_refreshing = True
        count = 0
        time
        await asyncio.sleep(0.5)
        start_time = time.time()
        try:
            while True:
                # 1. 使用 to_thread 运行耗时计算，防止界面卡死
                # 假设 calculate_lottery 是普通的同步函数
                # tempd, state = await asyncio.to_thread(self.calculate_lottery)
                tempd, state = await asyncio.to_thread(self.calculate_lottery)
                if state:
                    # 成功情况
                    self.tempd = tempd
                    self.showNumber.controls = self.displayNumbers(tempd).controls
                    self.tips_value("Search successful.", DraculaColors.GREEN)
                    self.state_exp = "done"
                    self.update()
                    break  # 成功后直接跳出循环
                else:
                    # 失败但未达到上限，更新 UI 并稍作等待
                    self.showNumber.controls = self.displayNumbers(tempd).controls
                    # self.showNumber.color = DraculaColors.ORANGE
                    self.buildBadge.content.value = f"{count}"
                    self.tips_value(
                        "We are searching diligently, please wait...",
                        DraculaColors.ORANGE,
                    )
                    self.state_exp = "ref"
                    self.update()
                    await asyncio.sleep(0.1)  # 给 CPU 喘息时间，也让 UI 有机会渲染
                count += 1
                elapsed_time = time.time() - start_time
                if elapsed_time >= self.timeout:
                    self.tips_value(
                        "Count is max_retries, work stoping.", DraculaColors.RED
                    )
                    self.state_exp = "none"
                    self.update()
                    break
        except Exception as e:
            # 显示错误/超时界面
            self.tips_value("Program execution error.", DraculaColors.YELLOW)
            self.update()
        finally:
            self.is_refreshing = False

    # endregion

    def calculate_lottery(self):
        settings = self.page.session.store.get("settings")
        filters = self.page.session.store.get("filters")
        if settings:
            rd = randomData(seting=settings["randomData"])
        else:
            return ("No settings", False)
        result = rd.get_pabc()
        if not filters:
            return (rd.get_exp(result), True)
        filter_jp = filter_for_pabc(filters=filters)
        if filter_jp.handle(result) == False:
            return (rd.get_exp(result), False)
        return (rd.get_exp(result), True)

    def handle_refresh_data(self, e):
        """右滑逻辑：刷新数据"""
        logr.info("向右滑动：正在刷新数据...")
        self.refresh(name="refresh_data")

    def handle_delete(self, e):
        if self.is_refreshing or self.selected:
            return
        if self.Itemc2_remove:
            self.Itemc2_remove(self)
        logr.info("点击了删除图标")


# endregion


# region itemsList
class itemsList(ft.Container):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()
        self.max_item = 10
        self.padding = 10
        self.width = float("inf")
        self.bgcolor = ft.Colors.TRANSPARENT

    def did_mount(self):
        self.running = True
        self.find_the_maximum()

    def will_unmount(self):
        self.running = False

    def find_the_maximum(self):
        is_mobile_or_web = self.page.web or self.page.platform in [
            ft.PagePlatform.ANDROID,
            ft.PagePlatform.IOS,
        ]
        self.max_item = 10 if is_mobile_or_web else 1000

    def add_itemc2(self, itemc2remove=None):
        control = self.content
        if not isinstance(control, ft.Column):
            logr.info(f"add_item type {type(control)}")
            return
        itemc2_len = [
            x for x in control.controls if isinstance(x, itemC2plus)
        ].__len__()
        if itemc2_len < self.max_item:
            temp = itemC2plus()
            temp.setting_Itemc2_Remove(itemc2remove)
            control.controls.append(temp)
            logr.info("Add itemC2plus")
            self.update()

    def all_refresh(self):
        """全部刷新"""
        control = self.content
        if not isinstance(control, ft.Column):
            logr.info(f"all_refresh {type(control)}")
            return
        itemc2_all = [x for x in control.controls if isinstance(x, itemC2plus)]
        for item in itemc2_all:
            if item.selected == False:
                item.refresh(name="all_refresh")

    def get_item_exp(self):
        """"""
        control = self.content
        if not isinstance(control, ft.Column):
            logr.info(f"all_refresh {type(control)}")
            return
        exp_all = [
            x.tempd
            for x in control.controls
            if isinstance(x, itemC2plus) and x.selected
        ]
        return exp_all

    def remove_item(self, item: itemC2plus):
        control = self.content
        if not isinstance(control, ft.Column):
            return
        if item:
            control.controls.remove(item)
            self.update()

    def __build_card(self):
        """Add, Apply, Cancel"""
        return ft.Column(
            # wrap=True,
            controls=[],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
        )


# endregion


# region commandList
class commandList(ft.Card):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()
        self.item_list_add = None
        self.itemc2remove = None
        self.all_refresh = None
        self.shot_capture = None

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def __build_card(self):
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=400,
            border=ft.Border.all(1, DraculaColors.COMMENT),
            bgcolor=DraculaColors.CRADBG,
            border_radius=10,
            content=self.__command_button(),
        )

    def setting_shot_capture(self, capture=None):
        self.shot_capture = capture

    def setting_item_list_add(self, itemlistadd=None, itemc2remove=None):
        self.item_list_add = itemlistadd
        self.itemc2remove = itemc2remove

    def setting_all_refresh(self, all_refresh=None):
        self.all_refresh = all_refresh

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            controls=[
                ft.TextButton(
                    key="add_close",
                    icon=ft.Icons.INSERT_EMOTICON,
                    content="Add",
                    on_click=self.handle_add,
                ),
                ft.TextButton(
                    icon=ft.Icons.REFRESH,
                    content="Refresh",
                    on_click=self.handle_refresh,
                ),
                ft.TextButton(
                    icon=ft.Icons.SAVE_AS,
                    content="Export",
                    on_click=self.handle_export,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )

    def handle_export(self):
        if self.shot_capture:
            self.page.run_task(self.shot_capture)

    def handle_add(self):
        """执行add"""
        if self.item_list_add and self.itemc2remove:
            self.item_list_add(self.itemc2remove)

    def handle_refresh(self):
        if self.all_refresh:
            self.all_refresh()


# endregion


# region luck_tips
class lucktips(ft.Container):
    def __init__(self):
        super().__init__()
        self.bgcolor = ft.Colors.TRANSPARENT
        self.width = float("inf")
        self.padding = 10
        self.content = self.__build_tips()

    def __build_text(self, text: str = "Luck word."):
        return ft.Text(
            value=f"{text}",
            size=15,
            color=ft.Colors.with_opacity(0.5, DraculaColors.FOREGROUND),
            max_lines=2,
        )

    def __build_tips(self):
        content = ft.Column(
            controls=[
                self.__build_text(
                    "愿你所有的好运都不期而遇，愿你所有的努力都有岁月的温柔回馈。✨"
                ),
                self.__build_text(
                    "May all the good luck come to you unexpectedly, and may all your hard work be rewarded with the gentleness of time. 🕊️"
                ),
            ],
        )
        return content


# endregion


# region LotteryPage
class LotteryPage:
    def __init__(self):

        self.itemslist = itemsList()
        self.comandlist = commandList()
        self.serendipitous_Capture = serendipitousCapture()

        self.serendipitous_Capture.setting_get_exp_all(self.itemslist.get_item_exp)
        self.comandlist.setting_item_list_add(
            self.itemslist.add_itemc2, self.itemslist.remove_item
        )
        self.comandlist.setting_shot_capture(
            self.serendipitous_Capture.schot_exp_capture
        )
        self.comandlist.setting_all_refresh(self.itemslist.all_refresh)
        self.luckTips = lucktips()
        self.view = self.get_data_view()

    # region get_data_view
    def get_data_view(self):
        return ft.Column(
            controls=[
                # ft.Image(
                #     src="lotter.png",
                #     fit=ft.BoxFit.FIT_HEIGHT,
                #     width=288 * 0.45,
                #     height=131 * 0.45,
                # ),
                ft.Text(
                    "Lotter",
                    size=25,
                    weight="bold",
                    color=DraculaColors.COMMENT,
                    font_family="RacingSansOne-Regular",
                ),
                ft.Divider(),
                self.luckTips,
                self.itemslist,
                self.serendipitous_Capture,
                self.comandlist,
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )

    # endregion


# endregion
