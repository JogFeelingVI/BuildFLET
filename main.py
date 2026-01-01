# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-01 14:36:16

from Customs.setings import Selectable
from Customs.filter import get_filter_view
import flet as ft
import json
import os

# 获取系统标示
app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


def main(page: ft.Page):
    page.title = "Jackpot App"
    page.theme_mode = ft.ThemeMode.DARK
    # 设置移动端适配的内边距
    page.padding = ft.Padding.only(bottom=20)
    page.ScrollMode = "hidden"

    # --- 页面逻辑控制 ---
    def on_navigation_change(e):
        index = e.control.selected_index
        # 切换中间的内容区域
        if index == 0:
            content_area.content = setting_view
        elif index == 1:
            content_area.content = filter_view
        elif index == 2:
            content_area.content = data_view
        page.update()

    def read_from_json():
        json_data = {}
        select_pn = []
        try:
            with open(jackpot_seting, "r") as f:
                json_data = json.load(f)
            for k, item in json_data["randomData"].items():
                if k == "note":
                    continue
                temp = Selectable().set_json(k, item)
                select_pn.append(temp)
        except Exception as e:
            json_data = {}

        if select_pn.__len__() == 0:
            for k in ["PA", "PB", "PC"]:
                select_pn.append(Selectable(k))
        return select_pn

    selectPx = read_from_json()

    def save_to_json():
        json_data = {"randomData": {"note": "setings json code save_to_json()"}}
        for sPn in selectPx:
            json_data["randomData"].update(sPn.get_json())

        with open(jackpot_seting, "w") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)

        # snack_bar
        snack_bar = ft.SnackBar(
            content=ft.Text(
                f"Settings have been saved successfully.",
                style=ft.TextStyle(color="WHITE"),
            ),
            bgcolor="PINK",
        )
        page.show_dialog(snack_bar)
        page.update()

    # Setting 页面
    setting_view = ft.Column(
        controls=[
            ft.Text("Setings", size=25, weight=ft.FontWeight.BOLD),
            # 彩票选择
            *selectPx,
            ft.Divider(height=5),
            ft.Row(
                controls=[
                    ft.Button(
                        "Save Steings",
                        icon=ft.Icons.SAVE,
                        icon_color=ft.Colors.WHITE,
                        color=ft.Colors.WHITE,
                        on_click=save_to_json,
                        style=ft.ButtonStyle(
                            bgcolor="PINK", shape=ft.RoundedRectangleBorder(radius=10)
                        ),
                    )
                ],
                alignment="END",
            ),
        ],
        scroll=ft.ScrollMode.ADAPTIVE,
        expand=True,
        alignment=ft.MainAxisAlignment.START,
    )

    # Filter 页面
    # filter_view = ft.Column(
    #     controls=[
    #         ft.Text("Filter", size=25, weight=ft.FontWeight.BOLD),
    #         ft.Text("Add various filtering criteria here:"),
    #         ft.TextField(label="关键词过滤", prefix_icon=ft.Icons.FILTER_2_SHARP),
    #         ft.Dropdown(
    #             label="分类筛选",
    #             options=[
    #                 ft.dropdown.Option("选项 1"),
    #                 ft.dropdown.Option("选项 2"),
    #             ],
    #         ),
    #         ft.Checkbox(label="仅显示有效数据"),
    #     ],
    #     expand=True,
    # )

    filter_view = get_filter_view(page)

    # Data 页面
    data_view = ft.Column(
        controls=[
            ft.Text("Data", size=25, weight=ft.FontWeight.BOLD),
            ft.Text("显示筛选后的结果："),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("ID")),
                    ft.DataColumn(ft.Text("结果")),
                ],
                rows=[
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("1")),
                            ft.DataCell(ft.Text("数据 A")),
                        ]
                    ),
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text("2")),
                            ft.DataCell(ft.Text("数据 B")),
                        ]
                    ),
                ],
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.ADAPTIVE,
    )

    # --- 2. 界面组件定义 ---

    # 中间显示区域容器
    content_area = ft.Container(
        content=setting_view,  # 默认显示设置页
        expand=True,
        padding=20,
    )

    # 底部 NavigationBar
    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(
                icon=ft.Icons.SETTINGS_OUTLINED,
                selected_icon=ft.Icons.SETTINGS,
                label="Setting",
            ),
            ft.NavigationBarDestination(icon=ft.Icons.FILTER_LIST_ALT, label="Filter"),
            ft.NavigationBarDestination(
                icon=ft.Icons.DATA_EXPLORATION_OUTLINED, label="Data"
            ),
        ],
        on_change=on_navigation_change,
    )

    # 将内容添加到页面
    page.add(content_area)
    page.update()


# 运行应用
ft.run(main)
