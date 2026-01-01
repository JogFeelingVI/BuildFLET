# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-01 12:20:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-01 14:26:31

import re
import flet as ft
import os
import json

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")

def get_filter_view(page: ft.Page):
    filters_list = []
    editing_index = -1

    filter_items_column = ft.Column(spacing=10)

    # --- 1. 定义 Target 下拉列表 ---
    target_dropdown = ft.Dropdown(label="Target", width=400)

    # --- 2. 定义 Conditions 自动填充输入框 ---
    # 定义一些建议项
    suggestions = [
        ft.AutoCompleteSuggestion(key="> 100", value="大于 100"),
        ft.AutoCompleteSuggestion(key="< 50", value="小于 50"),
        ft.AutoCompleteSuggestion(key="== 'Active'", value="状态为 Active"),
        ft.AutoCompleteSuggestion(key="between 10 and 20", value="在 10 到 20 之间"),
    ]

    condition_input = ft.AutoComplete(
        suggestions=suggestions,
        # placeholder="Enter or select filter criteria.",
        on_select=lambda e: print(f"Selected: {e.selection}"),
    )

    # --- 逻辑处理 ---

    def refresh_target_options():
        if os.path.exists(jackpot_seting):
            with open(jackpot_seting, "r") as f:
                data = json.load(f)
                # 3. 解析嵌套结构
                # 目标是获取 PA, PB, PC 等 key
                random_data = data.get("randomData", {})
                print(f'{random_data=}')
                
                enabled_tags = []
                for key, content in random_data.items():
                    # 排除 'note' 字段，并且只添加 enabled 为 True 的项
                    if isinstance(content, dict) and content.get("enabled") is True:
                        enabled_tags.append(key)
                # 4. 更新下拉菜单选项
                target_dropdown.options = [ft.dropdown.Option(tag) for tag in enabled_tags]
                
                if not enabled_tags:
                    target_dropdown.hint_text = "No activation option available."
        page.update()

    def handle_apply(e):
        nonlocal editing_index
        # 注意：AutoComplete 的文本值通过 text_field 的 value 获取，
        # 但在 Flet 中，直接访问 condition_input.value 即可
        val = condition_input.value

        if not target_dropdown.value or not val:
            return

        new_data = {"target": target_dropdown.value, "condition": val}

        if editing_index == -1:
            filters_list.append(new_data)
        else:
            filters_list[editing_index] = new_data

        dlg.open = False
        render_filters()
        page.update()

    def open_dialog(index=-1):
        nonlocal editing_index
        editing_index = index
        refresh_target_options()

        if index != -1:
            item = filters_list[index]
            target_dropdown.value = item["target"]
            condition_input.value = item["condition"]  # 回填 AutoComplete
        else:
            target_dropdown.value = None
            condition_input.value = ""  # 重置 AutoComplete

        dlg.open = True
        page.update()

    def render_filters():
        filter_items_column.controls.clear()
        for idx, item in enumerate(filters_list):
            filter_items_column.controls.append(
                ft.Dismissible(
                    content=ft.ListTile(
                        leading=ft.Icon(ft.Icons.FILTER_ALT),
                        title=ft.Text(f"Target: {item['target']}"),
                        subtitle=ft.Text(f"Condition: {item['condition']}"),
                        bgcolor=ft.Colors.BLACK_12,
                        on_long_press=lambda _, i=idx: open_dialog(i),
                    ),
                    on_dismiss=lambda _, i=idx: remove_filter(i),
                    dismiss_direction=ft.DismissDirection.START_TO_END,
                    background=ft.Container(
                        bgcolor=ft.Colors.RED_ACCENT,
                        content=ft.Text("Delete", color="white", weight="bold"),
                        alignment=ft.Alignment.CENTER_LEFT,
                        padding=20,
                    ),
                )
            )

    def remove_filter(index):
        filters_list.pop(index)
        render_filters()
        page.update()

    # --- 对话框组装（这里使用了 condition_input） ---
    dlg = ft.AlertDialog(
        title=ft.Text("Filter Settings"),
        content=ft.Column(
            [
                target_dropdown,
                ft.Text("Conditions:", size=12, color=ft.Colors.GREY_700),
                condition_input,  # 将 AutoComplete 放入对话框
            ],
            tight=True,
            spacing=10,
        ),
        actions=[
            ft.TextButton(
                "Cancel",
                on_click=lambda _: setattr(dlg, "open", False) or page.update(),
            ),
            ft.Button(
                "Apply",
                bgcolor=ft.Colors.RED,
                color=ft.Colors.WHITE,
                on_click=handle_apply,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dlg)

    return ft.Column(
        controls=[
            ft.Text("Filter", size=25, weight=ft.FontWeight.BOLD),
            ft.Button(
                "Add Filter", icon=ft.Icons.ADD, on_click=lambda _: open_dialog(-1)
            ),
            ft.Divider(),
            ft.Column(
                [filter_items_column], scroll=ft.ScrollMode.ADAPTIVE, expand=True
            ),
        ],
        expand=True,
    )
