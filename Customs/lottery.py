# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-04 07:17:43

from .jackpot_core import randomData
from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
import flet as ft
import json
import os
import time

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")

def calculate_lottery(setings:dict,filters:dict):
    if setings:
        rd = randomData(seting=setings)
    else:
        return None
    result = rd.get_pabc()
    print(f'calculate_lottery: {result = }')
    if filters:
        pass
    else:
        pass
    result = rd.get_exp(result)
    return result
    

class LotteryPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.buttons = self.set_Lotter_buttons()
        self.lottery_items_column = ft.Column(spacing=10)
        self.view = self.get_data_view()
    
    def set_Lotter_buttons(self):
        Lottery_item_count_data = {
            "2":2,
            "5":5,
            "10":10,
            "15":15
        }
        button_list = []
        for key, item in Lottery_item_count_data.items():
            button_list.append(
                ft.Button(
                    f"{key} items",
                    tooltip=ft.Tooltip(message=f"Set the number of lottery tickets to obtain to {key}."),
                    # 【重要】使用默认参数 data=item 来破解 Lambda 闭包陷阱
                    on_click=lambda e,data=item: self.save_Lottery_item(data),
                )
            )
        return button_list
            
    def save_Lottery_item(self,data:int):
        self.page.session.store.set("Lottery_item_count",data)
    
    def Get_Lottery_data(self, index:int):
        Lottery_items_count = self.page.session.store.get("Lottery_item_count")
        setings = self.page.session.store.get('setings')
        Progress = ft.ProgressBar(year_2023=True,color=Dracula_colors.PINK)
        self.lottery_items_column.controls.append(Progress)
        results = []
        while len(results) != Lottery_items_count:
            result = calculate_lottery(setings=setings["randomData"], filters=None)
            Progress.value = len(result) * (100/Lottery_items_count)
            results.append(result)
            self.page.update()
        self.lottery_items_column.controls.clear()
        for res in results:
            exp_control = ft.ListTile(
                    leading=ft.Icon(ft.Icons.STAR, color=Dracula_colors.RED),
                    title=ft.Text(
                        f"{randomData.generate_secure_string()}",
                    ),
                    subtitle=ft.Text(
                        f"Number: {res}",
                        weight="bold",
                        color=Dracula_colors.COMMENT
                    ),
                )
            self.lottery_items_column.controls.append(exp_control)
        self.page.update()

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
