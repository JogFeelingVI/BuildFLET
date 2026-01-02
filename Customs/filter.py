# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-01 12:20:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-02 00:58:34

import flet as ft
import os
import json

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


def get_filter_view(page: ft.Page):
    filters_list = []
    editing_index = -1
    last_selected_target = None

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
        """读取配置并刷新下拉列表，返回当前可用的标签列表"""
        global jackpot_seting

        enabled_tags = []

        if os.path.exists(jackpot_seting):
            try:
                with open(jackpot_seting, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    random_data = data.get("randomData", {})
                    for key, content in random_data.items():
                        if isinstance(content, dict) and content.get("enabled") is True:
                            enabled_tags.append(key)
            except Exception:
                pass

        # 更新下拉菜单选项
        target_dropdown.options = [ft.dropdown.Option(tag) for tag in enabled_tags]
        return enabled_tags

    def handle_apply(e):
        nonlocal editing_index, last_selected_target

        if not target_dropdown.value or not condition_input.value:
            return

        # 保存本次的选择，以便下次 Add 时默认选中
        last_selected_target = target_dropdown.value

        new_data = {"target": target_dropdown.value, "condition": condition_input.value}

        if editing_index == -1:
            filters_list.append(new_data)
        else:
            filters_list[editing_index] = new_data

        dlg.open = False
        print("Applied:", filters_list)
        render_filters()
        page.update()

    def open_dialog(index=-1):
        nonlocal editing_index, last_selected_target
        editing_index = index
        available_tags = refresh_target_options()

        if index == -1:
            # --- 新增模式 (Add Filter) ---
            # 优先级 1: 如果有上一次记录的选择，且该选择目前依然在启用列表中，则继续使用它
            if last_selected_target in available_tags:
                target_dropdown.value = last_selected_target
            # 优先级 2: 否则，如果列表不为空，默认选择第一项
            elif available_tags:
                target_dropdown.value = available_tags[0]
            else:
                target_dropdown.value = None

            condition_input.value = ""  # 新增时清空输入框
        else:
            # --- 编辑模式 (Long Press) ---
            item = filters_list[index]
            # 确保保存的值还在当前启用列表中，否则下拉框会显示空白
            target_dropdown.value = (
                item["target"] if item["target"] in available_tags else None
            )
            condition_input.value = item["condition"]

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
                "Add filtering rules",
                icon=ft.Icons.ADD,
                on_click=lambda _: open_dialog(-1),
            ),
            ft.Divider(),
            ft.Column([filter_items_column], scroll=ft.ScrollMode.HIDDEN, expand=True),
        ],
        expand=True,
        scroll=ft.ScrollMode.HIDDEN,
    )
