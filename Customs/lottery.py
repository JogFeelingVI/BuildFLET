# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-06 05:38:16

from .jackpot_core import randomData
from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
import flet as ft
import json
import os
import asyncio

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


def calculate_lottery(setings: dict, filters: dict):
    if setings:
        rd = randomData(seting=setings)
    else:
        return None
    result = rd.get_pabc()
    if filters:
        pass
    else:
        pass
    result = rd.get_exp(result)
    return result


class lottery_items(ft.Column):
    def __init__(self):
        super().__init__()
        self.progress = ft.ProgressBar(
            year_2023=True, color=Dracula_colors.PINK, value=0, visible=False
        )
        self.spacing = 2
        self.controls.append(self.progress)
        self.results = []

    def did_mount(self):
        # 此时 self.page 已经可用了
        self.runing = True
        self.update()

    def will_unmount(self):
        self.runing = False

    def cilcked(self, setting: dict):
        if not setting and self.runing:
            return
        self.lottery_items_count = (
            self.page.session.store.get("Lottery_item_count") or 10
        )
        self.settings = setting
        self.page.run_task(self.update_progress)

    async def update_progress(self):
        self.progress.visible = True
        self.controls.clear()
        self.controls.append(self.progress)
        count = self.lottery_items_count
        while count:
            self.results.append(calculate_lottery(setings=self.settings, filters=None))
            self.progress.value = (
                self.lottery_items_count - count + 1
            ) / self.lottery_items_count
            count -= 1
            self.update()
            await asyncio.sleep(0.1)
        self.progress.visible = False
        while self.results:
            item = self.results.pop()
            self.controls.append(
                ft.ListTile(
                    leading=ft.Icon(
                        ft.Icons.GENERATING_TOKENS, color=Dracula_colors.RED
                    ),
                    title=ft.Text(
                        f"{randomData.generate_secure_string()}",
                        color=Dracula_colors.COMMENT,
                        size=11,
                    ),
                    subtitle=ft.Text(
                        f"{item}",
                        weight="bold",
                        size=18,
                        color=Dracula_colors.PURPLE,
                    ),
                )
            )
            self.update()
            await asyncio.sleep(0.1)


class LotteryPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.buttons = self.set_Lotter_buttons()
        self.lottery_items_column = lottery_items()
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
            self.lottery_items_column.cilcked(settings["randomData"])
        except Exception:
            self.page.show_dialog(
                get_snack_bar("Failed to retrieve settings data.", "error")
            )

    def get_data_view(self):
        self.save_Lottery_item(5)
        return ft.Column(
            controls=[
                ft.Text(
                    "Lottery",
                    size=25,
                    weight=ft.FontWeight.BOLD,
                    color=Dracula_colors.COMMENT,
                ),
                ft.Button(
                    "Get lottery results",
                    icon=ft.Icons.SHOW_CHART,
                    on_click=lambda _: self.Get_Lottery_data(-1),
                ),
                ft.Divider(),
                ft.Row(controls=self.buttons, scroll=ft.ScrollMode.HIDDEN, expand=True),
                ft.Divider(),
                ft.Column(
                    self.lottery_items_column,
                    scroll=ft.ScrollMode.HIDDEN,
                    expand=True,
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
