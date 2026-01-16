# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-16 03:10:40

from .lotteryballs import LotteryBalls
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
        self.initial_count = 0
        self.lottery_icon = ft.Icon(
            icon=ft.Icons.MONEY, color=Dracula_colors.FOREGROUND
        )

        # self.Fab = ft.FloatingActionButton(
        #     icon=self.lottery_icon,
        #     bgcolor=Dracula_colors.ORANGE,
        #     on_click=lambda _: self.Get_Lottery_data(-1),
        #     tooltip="click:add now DISM,long prass: save data.",
        #     # opacity=0.65,
        # )

        self.Fab = ft.GestureDetector(
            content=ft.Container(
                content=self.lottery_icon,
                padding=15,
                bgcolor=Dracula_colors.ORANGE,
                width=56,
                height=56,
                border_radius=ft.border_radius.all(16),  # 圆形
                alignment=ft.Alignment.CENTER,
                # 添加阴影，使其看起来像悬浮按钮
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=10,
                    color="#42000000",
                    offset=ft.Offset(0, 2),
                ),
            ),
            mouse_cursor=ft.MouseCursor.CLICK,
            on_tap=lambda _: self.Get_Lottery_data(-1),
            on_long_press=self.inisatll_save_dig,
        )

        self.lottery_items_column = ft.Column(
            spacing=1, scroll=ft.ScrollMode.HIDDEN, expand=True
        )
        self.view = self.get_data_view()
        self.page.run_task(self.initialize_data)

    async def inisatll_save_dig(self, e):
        print(f"kaishi Save. {self.saved_data}")
        data_row = [ft.Text("Save List len is zero.")]
        if self.saved_data.__len__() != 0:
            data_row.clear()
        else:
            self.page.show_dialog(
                get_snack_bar("No data to save.", "error")
            )
            return
        count = 0
        max_count = 10
        items =[]
        while count < max_count:
            item = self.saved_data.pop(0)
            items.append(item)
            data_row.append(
                ft.Container(
                    content=LotteryBalls(item,ball_size=29, align="LE"),
                    padding=5,)
            )
            count += 1
            if self.saved_data.__len__() == 0:
                break
        
        await self.page.shared_preferences.set(
                    "save_data_list", json.dumps(self.saved_data)
                )
        await self.initialize_data()

        BottomSheet = ft.BottomSheet(
            scrollable=True,
            bgcolor=Dracula_colors.CURRENT_LINE,
            content=ft.Screenshot(
                content=ft.Container(
                    content=ft.Column(
                        tight=True,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                value="JackPot",
                                size=30,
                                weight="bold",
                                color=Dracula_colors.PINK,
                            ),
                            ft.Divider(color=Dracula_colors.PURPLE),
                            *data_row,
                            ft.Divider(color=Dracula_colors.PURPLE),
                            ft.Row(
                                controls=[
                                    ft.TextButton(
                                        content="Save",
                                    ),
                                    ft.TextButton(
                                        content="Cancel",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    padding=20,
                    width=400,
                    # height=680,
                    alignment=ft.Alignment.TOP_CENTER,
                )
            ),
            on_dismiss=self.dismiss_save_data
        )
        self.page.show_dialog(BottomSheet)
    
    def dismiss_save_data(self):
        self.page.run_task(self.initialize_data)
        self.Badge_number(self.initial_count)

    async def initialize_data(self):
        """异步加载初始数据并渲染"""
        raw_json = await self.page.shared_preferences.get("save_data_list")
        self.saved_data = json.loads(raw_json) if raw_json else []
        self.initial_count = len(self.saved_data)
        # self.lottery_icon.badge =str(self.initial_count) if self.initial_count > 0 else None
        if self.initial_count == 0:
            self.lottery_icon.badge.label_visible=False
            return
        self.lottery_icon.badge = ft.Badge(
            label=str(self.initial_count) if self.initial_count > 0 else None,
            bgcolor=Dracula_colors.PINK,
            text_color=Dracula_colors.FOREGROUND,
            # offset=ft.Offset(18, -18),
        )
        self.Fab.update()

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

    def Badge_number(self, lens: int = 0):
        self.page.run_task(self.initialize_data)
        if lens == 0:
            return
        for nbar in self.page.navigation_bar.destinations:
            if isinstance(nbar, ft.NavigationBarDestination) and nbar.label == "Lotter":
                nbar.icon.badge = lens
        # self.page.update()

    def Get_Lottery_data(self, index: int):
        print(f"Get_Lottery_data is runing {index=}")
        try:
            settings = self.page.session.store.get("settings")
            filters = self.page.session.store.get("filters")
            lic = self.page.session.store.get("Lottery_item_count") or 5
            for isdism in self.lottery_items_column.controls:
                if not isdism:
                    continue
                if isinstance(isdism, dism):
                    if isdism.is_refreshing:
                        self.page.show_dialog(
                            get_snack_bar(
                                "The DISM tasks were not all completed.", "error"
                            )
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
