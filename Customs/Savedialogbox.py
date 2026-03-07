# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-02 09:10:57
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-07 13:56:51

from .jackpot_core import randomData, filter_for_pabc
from .DraculaTheme import DraculaColors, RandColor
from .adbox import adbx
import asyncio
import flet as ft
import datetime


# region _savedialog
class _savedialog:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten)
        self.adb.setting_did_mount_callback(self.load_exp)
        self.exps_is_build = True
        self.getallexp = None

    def seting_get_all_exp(self, getallexp=None):
        self.getallexp = getallexp

    def __builde_conter(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.genid = randomData.generate_secure_string(8)
        footer = ft.Row(
            controls=[
                ft.Text(f"{now} {self.genid}", size=14, color=DraculaColors.ORANGE)
            ],
            alignment=ft.MainAxisAlignment.END,
        )
        title = ft.Text(
            "Jackpot Lotter",
            size=28,
            weight="bold",
            font_family="RacingSansOne-Regular",
            color=DraculaColors.ORANGE,
            italic=True,
        )
        self.exps = ft.Column(
            spacing=5,
        )
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.TextButton(
                    "Cancel",
                    on_click=self.__handle_cancel,
                    style=ft.ButtonStyle(color=RandColor()),
                ),
                # 确定按钮用红色突出显示危险操作
                ft.TextButton(
                    "Save to png",
                    on_click=self.__handle_save,
                    style=ft.ButtonStyle(color=RandColor()),
                ),
            ],
        )

        conter = ft.Container(
            # width=400,
            padding=5,
            border_radius=0,
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
        self.Screenshot = ft.Screenshot(content=conter)
        content = ft.Column(
            controls=[self.Screenshot],
            tight=True,
        )
        return content

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
            items.append(self.CreateItem(_exp, i))
            if (i + 1) % 5 == 0 and (i + 1) < len(_exp):
                items.append(self.CreateItem("", -1))
        self.exps.controls = items
        self.exps.update()
        self.exps_is_build = True

    def __handle_cancel(self):
        if self.adb.running:
            self.adb.page.pop_dialog()

    def CreateItem(self, text: str = "", i=0):
        userColor = RandColor(mode="def")
        asize = 18
        item = (
            ft.Container(
                padding=5,
                # border=ft.Border.all(1, ft.Colors.with_opacity(0.4, userColor)),
                bgcolor=ft.Colors.with_opacity(0.1, userColor),
                border_radius=5,
                content=ft.Row(
                    wrap=True,
                    width=float("inf"),
                    spacing=5,
                    controls=[
                        ft.Container(
                            content=ft.Text(
                                f"{chr(65 + i)}",
                                size=asize * 0.6,
                                text_align=ft.TextAlign.CENTER,
                                color=DraculaColors.FOREGROUND,
                            ),
                            alignment=ft.Alignment.CENTER,
                            border_radius=asize / 2,
                            border=ft.Border.all(
                                1, ft.Colors.with_opacity(0.8, userColor)
                            ),
                            bgcolor=ft.Colors.with_opacity(0.2, userColor),
                            width=asize,
                            height=asize,
                        ),
                        ft.Text(
                            f"{text}",
                            size=asize,
                            weight=ft.FontWeight.BOLD,
                            color=userColor,
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
                png_name = f"{self.genid}.png"
                # print(f"{image.__sizeof__()=} {png_name=}")

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
                # print(f"Image saving error.")
                pass
            finally:
                await asyncio.sleep(1)
                self.adb.page.pop_dialog()


# endregion


# region _tadbx
class _tadbx:
    def __init__(self):
        self.conten = self.__builde_conter()
        self.adb = adbx(None, self.conten)

    def __handle_Close(self, e):
        if self.adb.running:
            self.adb.page.pop_dialog()

    def __handle_start(self, e):
        if self.adb.running:
            self.adb.page.run_task(self.start_testing)

    async def start_testing(self):
        if not self.adb.running:
            return
        settings = self.adb.page.session.store.get("settings")
        filtersAll = self.adb.page.session.store.get("filters")
        self.info_display.controls.clear()
        if not filtersAll:
            self.info_display.controls.append(self.info("filters is Null."))
            self.info_display.update()
            return
        if settings and filtersAll:
            _rdpn = randomData(seting=settings["randomData"])
            results = []
            for i in range(1000):
                results.append(_rdpn.get_pabc())
        filed = []
        for _fitem in filtersAll:
            # print(f"{_fitem}")
            _f2func = filter_for_pabc(filters=[_fitem])
            pass_rate = (
                sum([1 for r in results if _f2func.handle(r)]) / len(results) * 100
            )
            prinfo = [
                f"{_fitem['func']}",
                f"{_fitem['target']}",
                f"{_fitem['condition']}",
                f"{pass_rate:.0f}",
            ]
            filed.append(prinfo)
        sorted_data = sorted(filed, key=lambda x: x[-1])
        max_num = max(item[-1] for item in sorted_data)
        min_num = min(item[-1] for item in sorted_data)
        for _s in list(sorted_data)[0:10]:
            self.info_display.controls.append(self.info(*_s))
        zuida = f"Max {max_num} Min: {min_num} filters len {len(filtersAll)}"
        self.info_display.controls.append(self.info(zuida))
        self.info_display.update()

    def __builde_conter(self):
        title = ft.Text(
            "Filter test",
            size=28,
            weight="bold",
            font_family="RacingSansOne-Regular",
            color=DraculaColors.ORANGE,
            italic=True,
        )
        self.info_display = ft.Column(
            tight=True,
            spacing=3,
            scroll=ft.ScrollMode.HIDDEN,
            controls=[
                ft.Text("Click the `Start testing` to begin the test."),
            ],
        )
        acts = ft.Row(
            alignment=ft.MainAxisAlignment.END,
            controls=[
                ft.TextButton(
                    "Close",
                    on_click=self.__handle_Close,
                    style=ft.ButtonStyle(color=RandColor()),
                ),
                # 确定按钮用红色突出显示危险操作
                ft.TextButton(
                    "Start testing",
                    on_click=self.__handle_start,
                    style=ft.ButtonStyle(color=RandColor()),
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
                controls=[title, self.info_display, acts],
            ),
        )
        return conter

    def info(self, *msg):
        bold = False
        size = 14
        spans = []
        for i, m in enumerate(msg):
            if i == len(msg) - 1:
                bold = True
                m = f"{m}%" if m != "0" else f"{m}% ✖"
            spans.append(
                ft.TextSpan(
                    f"{m} ",
                    style=ft.TextStyle(
                        size=size + 1 if bold else size - 1,
                        color=RandColor(mode="Morandi")
                        if bold
                        else ft.Colors.with_opacity(0.5, RandColor(mode="Morandi")),
                        weight="bold" if bold else None,
                        italic=bold,
                    ),
                )
            )
            bold = False
        conter = ft.Container(
            padding=0,
            content=ft.Row(
                spacing=5,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # ft.Icon(ft.Icons.INFO, size=size),
                    ft.Text(spans=spans),
                ],
            ),
        )
        return conter


# endregion
