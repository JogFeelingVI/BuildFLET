# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-03 09:47:48
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-16 08:03:47

import asyncio
from .jackpot_core import randomData
from .lotteryballs import LotteryBalls
from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
from .dismiss import dism
import flet as ft
import json
import os

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


class LotteryPage:
    def __init__(self, page: ft.Page):
        self.page = page
        self.user_dir = app_data_path
        self.buttons = self.set_Lotter_buttons()
        self.lottery_icon = ft.Icon(
            icon=ft.Icons.MONEY,
            color=Dracula_colors.FOREGROUND,
            badge=ft.Badge(
                label="0",
                bgcolor=Dracula_colors.COMMENT,
                text_color=Dracula_colors.FOREGROUND,
            ),
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
        raw_json = await self.page.shared_preferences.get("save_data_list")
        saved_data = json.loads(raw_json) if raw_json else []
        print(f"kaishi Save. {saved_data=}")
        data_row = [ft.Text("Save List len is zero.")]
        if saved_data.__len__() != 0:
            data_row.clear()
        else:
            self.page.show_dialog(get_snack_bar("No data to save.", "error"))
            return
        count = 0
        max_count = 7
        items = []
        while count < max_count:
            item = saved_data.pop(0)
            items.append(item)
            data_row.append(
                ft.Container(
                    content=LotteryBalls(item, ball_size=29, align="LE"),
                    padding=2,
                )
            )
            count += 1
            if saved_data.__len__() == 0:
                break

        await self.page.shared_preferences.set("save_data_list", json.dumps(saved_data))
        await self.initialize_data()

        async def handle_save(e):
            e.control.disabled = True
            self.page.update()
            path = await self.select_dir()
            if not path:
                print("No directory was selected; saving cancelled.")
                e.control.disabled = False
                self.page.update()
                return
            print(f"select dir is {self.user_dir=}")
            await self.save_screenshot(sc, path, genid)
            nonlocal items
            items.clear()
            # await self.initialize_data()
            await asyncio.sleep(0.5)
            self.Badge_number(0)
            e.control.disabled = False
            BottomSheet.open = False
            # self.page.update()

        def handle_cancel(e):
            BottomSheet.open = False
            self.page.update()

        genid = randomData.generate_secure_string(8)

        sc = ft.Screenshot(
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
                        ft.Row(
                            controls=[
                                ft.Text(
                                    value=f"GENID: {genid}",
                                    size=15,
                                    weight="bold",
                                    color=Dracula_colors.BACKGROUND,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.END,  # 关键点：主轴对齐到末尾
                        ),
                    ],
                ),
                bgcolor=Dracula_colors.CURRENT_LINE,
                padding=20,
                width=400,
                # height=680,
                alignment=ft.Alignment.TOP_CENTER,
            )
        )
        savebut = ft.Container(
            content=ft.Row(
                controls=[
                    ft.TextButton(
                        content="Save",
                        on_click=handle_save,
                    ),
                    ft.TextButton(
                        content="Cancel",
                        on_click=handle_cancel,
                    ),
                ],
            ),
            padding=ft.Padding(top=0, bottom=20, left=20, right=20),
            width=400,
        )

        BottomSheet = ft.BottomSheet(
            # scrollable=True,
            bgcolor=Dracula_colors.CURRENT_LINE,
            content=ft.Column(
                controls=[
                    sc,
                    savebut,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            on_dismiss=lambda _, data=items: self.handle_dismiss_save(data),
        )

        self.page.show_dialog(BottomSheet)

    async def select_dir(self):
        stored_dir = await self.page.shared_preferences.get("user_dir")
        if stored_dir:
            self.user_dir = stored_dir
            return self.user_dir

        if not self.page.web:
            picked_dir = await ft.FilePicker().get_directory_path(
                dialog_title="Please select a directory?"
            )
            if picked_dir:
                await self.page.shared_preferences.set("user_dir", picked_dir)
                self.user_dir = picked_dir
                return self.user_dir
        return self.user_dir

    async def save_screenshot(self, screenshot: ft.Screenshot, path, genid=""):
        image = await screenshot.capture()
        print(f"image data size: {len(image)} bytes")

        obj_path = os.path.join(path, f"jackpot_{genid}.png")
        print(f"saving screenshot to: {obj_path}")
        with open(obj_path, "wb") as f:
            f.write(image)

    def handle_cancel(self, bs: ft.BottomSheet):
        bs.open = False
        self.page.update()

    def handle_dismiss_save(self, data: list):
        self.page.run_task(self.dismiss_save_data, data)

    async def dismiss_save_data(self, data: list):
        raw_json = await self.page.shared_preferences.get("save_data_list")
        saved_data = json.loads(raw_json) if raw_json else []
        saved_data.extend(data)
        await self.page.shared_preferences.set("save_data_list", json.dumps(saved_data))
        self.page.run_task(self.initialize_data)
        # print(f'dismiss_save_data {saved_data=}')
        self.Badge_number(len(saved_data))

    async def initialize_data(self):
        """异步加载初始数据并渲染"""
        raw_json = await self.page.shared_preferences.get("save_data_list")
        saved_data = json.loads(raw_json) if raw_json else []
        initial_count = len(saved_data)
        self.lottery_icon.badge.label = f"{initial_count}"
        if self.lottery_icon.badge.label == "0":
            self.lottery_icon.badge.label_visible = False
        else:
            self.lottery_icon.badge.label_visible = True
        self.Fab.update()

    def Badge_number(self, lens: int = 0):
        self.page.run_task(self.initialize_data)
        for nbar in self.page.navigation_bar.destinations:
            if isinstance(nbar, ft.NavigationBarDestination) and nbar.label == "Lotter":
                if lens!=0:
                    nbar.icon.badge = str(lens)
                else:   
                    nbar.icon.badge = None
        self.page.update()

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
