# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-12 01:08:35

from .lotteryballs import LotteryBalls
from .jackpot_core import randomData, filter_for_pabc
from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
import flet as ft
import json
import os
import asyncio

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


def calculate_lottery(setings: dict, filters: list):
    if setings:
        rd = randomData(seting=setings)
    else:
        return ("No Numbers", False)
    result = rd.get_pabc()
    if not filters:
        return (rd.get_exp(result), True)
    filter_jp = filter_for_pabc(filters=filters)
    if filter_jp.handle(result) == False:
        return [rd.get_exp(result), False]
    return (rd.get_exp(result), True)


class listext_onlong(ft.Card):
    def __init__(self):
        super().__init__()
        self.data = "01 02 03 04 05 06 + 08"
        self.content = self.reContent(0)
        self.padding = 10
        # self.leading = ft.Icon(ft.Icons.GENERATING_TOKENS, color=Dracula_colors.ORANGE)
        # self.subtitle = LotteryBalls(self.data,25)
        # self.on_long_press = lambda _: self.get_data(1, True)
        self.runing = True
        self.is_refreshing = False

    def reContent(self, flg: int = 0):
        """
            返回 Container
        Args:
            flg (int, optional): _description_. Defaults to 0.
            0 Initializing the computing core.
            2 Please try again later.
            1 LotteryBalls
        Returns:
            _type_: _description_
        """
        if flg == 1:
            conten = LotteryBalls(self.data, 29)
        elif flg == 2:
            conten = ft.Row(
                controls=[
                    ft.Text(
                        "😡Press and hold to try again.",
                        weight="bold",
                        size=18,
                        color=Dracula_colors.PURPLE,
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                align=ft.Alignment.CENTER,
            )
        else:
            conten = ft.Row(
                controls=[
                    ft.Text(
                        "😅Initializing the computing core.",
                        weight="bold",
                        size=18,
                        color=Dracula_colors.CURRENT_LINE,
                    )
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                align=ft.Alignment.CENTER,
            )
        return ft.Container(
            padding=10,
            content=conten,
            animate_scale=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            on_long_press=lambda _: self.get_data(1, True),
        )

    def setting_args(self, setting: dict, filter: list):
        self.setting = setting
        self.filers = filter

    def did_mount(self):
        self.get_data(0)

    def will_unmount(self):
        self.runing = False

    def get_data(self, state: int = 1, onoff=False):
        # print(f'{self.content.scale=} {state=} {onoff=}')
        if self.is_refreshing:
            return
        if state == 0 and self.runing:
            self.page.run_task(self.refresh)
        if state == 1 and onoff:
            self.content.scale = ft.Scale(1.2)
            self.content.update()
            self.page.run_task(self.refresh)

    async def refresh(self):
        isok = False
        note_error = 0
        self.is_refreshing = True
        await asyncio.sleep(0.3)
        try:
            while isok == False:
                tempd, state = calculate_lottery(
                    setings=self.setting, filters=self.filers
                )
                if state:
                    self.data = tempd
                    self.content = self.reContent(1)
                    isok = state
                else:
                    if note_error >= 100:
                        self.content = self.reContent(2)
                        self.page.update()
                        break
                    note_error += 1
                    self.data = tempd
                    self.content = self.reContent(1)
                self.update()
                await asyncio.sleep(0.1)
        finally:
            self.is_refreshing = False


class LotteryPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.buttons = self.set_Lotter_buttons()
        self.Fab = ft.FloatingActionButton(
            icon=ft.Icons.MONEY,
            bgcolor=Dracula_colors.ORANGE,
            on_click=lambda _: self.Get_Lottery_data(-1),
            # opacity=0.65,
        )
        self.lottery_items_column = ft.Column(
            spacing=1, scroll=ft.ScrollMode.HIDDEN, expand=True
        )
        self.view = self.get_data_view()

    def set_Lotter_buttons(self):
        Lottery_item_count_data = {"2": 2, "5": 5, "10": 10, "15": 15}
        button_list = []
        for key, item in Lottery_item_count_data.items():
            button_list.append(
                ft.Button(
                    f"{key} items",
                    tooltip=ft.Tooltip(
                        message=f"Set the number of lottery tickets to obtain to {key}."
                    ),
                    # 【重要】使用默认参数 data=item 来破解 Lambda 闭包陷阱
                    on_click=lambda e, data=item: self.save_Lottery_item(data),
                )
            )
        return button_list

    def save_Lottery_item(self, data: int):
        self.page.session.store.set("Lottery_item_count", data)
        self.page.show_dialog(get_snack_bar(f"setting item count {data}"))

    def Get_Lottery_data(self, index: int):
        try:
            settings = self.page.session.store.get("settings")
            filters = self.page.session.store.get("filters")
            lic = self.page.session.store.get("Lottery_item_count") or 5
            self.lottery_items_column.controls.clear()
            for _ in range(lic):
                listext = listext_onlong()
                listext.setting_args(settings["randomData"], filters)
                self.lottery_items_column.controls.append(listext)
            # self.lottery_items_column.cilcked(settings["randomData"], filters=filters)
        except Exception:
            self.page.show_dialog(
                get_snack_bar("Failed to retrieve settings data.", "error")
            )

    def get_data_view(self):
        return ft.Column(
            controls=[
                ft.Text(
                    "Lottery",
                    size=25,
                    weight=ft.FontWeight.BOLD,
                    color=Dracula_colors.COMMENT,
                ),
                # ft.Button(
                #     "Get lottery results",
                #     icon=ft.Icons.SHOW_CHART,
                #     on_click=lambda _: self.Get_Lottery_data(-1),
                # ),
                ft.Divider(),
                ft.Row(controls=self.buttons, scroll=ft.ScrollMode.HIDDEN, expand=True),
                ft.Divider(),
                # ft.Column(
                #     self.lottery_items_column,
                #     scroll=ft.ScrollMode.HIDDEN,
                #     expand=True,
                # ),
                self.lottery_items_column,
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
