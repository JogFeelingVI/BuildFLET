# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-15 13:35:13

from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
from .dismiss import dism, listext_onlong
import flet as ft
import json
import os

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


class LotteryPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.buttons = self.set_Lotter_buttons()
        self.Fab = ft.FloatingActionButton(
            icon=ft.Icons.MONEY,
            bgcolor=Dracula_colors.ORANGE,
            on_click=lambda _: self.Get_Lottery_data(-1),
            tooltip="click:add now DISM,long prass: save data.",
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
        
    def Badge_number(self,lens:int=0):
        if lens == 0:
            return
        for nbar in self.page.navigation_bar.destinations:
            if isinstance(nbar,ft.NavigationBarDestination) and nbar.label == "Lotter":
                nbar.icon.badge=lens
        # self.page.update()

    def Get_Lottery_data(self, index: int):
        # print(f'Get_Lottery_data is runing {index=}')
        try:
            settings = self.page.session.store.get("settings")
            filters = self.page.session.store.get("filters")
            lic = self.page.session.store.get("Lottery_item_count") or 5
            for isdism in self.lottery_items_column.controls:
                if isinstance(isdism, dism):
                    if isdism.is_refreshing:
                        self.page.show_dialog(
                            get_snack_bar("The DISM tasks were not all completed.", "error")
                        )
                        return

            self.lottery_items_column.controls.clear()
            for _ in range(lic):
                # listext = listext_onlong()
                listext = dism()
                listext.setting_args(settings["randomData"], filters, self.Badge_number)
                self.lottery_items_column.controls.append(listext)
            # self.lottery_items_column.cilcked(settings["randomData"], filters=filters)
        except Exception as e:
            print(f"debug : {e}")
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
