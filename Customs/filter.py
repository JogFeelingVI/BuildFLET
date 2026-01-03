# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-01 12:20:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-03 11:58:15

from calendar import c
from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
import flet as ft
import os
import json

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


class FilterPage:
    """筛选页面类"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.filters_list = []
        self.editing_index = -1
        self.last_selected_target = None

        self.filter_items_column = ft.Column(spacing=10)
        # --- 1. 定义 Target 下拉列表 ---
        self.target_dropdown = ft.Dropdown(label="Target", width=400)
        self.condition_input = ft.AutoComplete(
            # suggestions=suggestions,
            # placeholder="Enter or select filter criteria.",
            on_select=lambda e: print(f"Selected: {e.selection}"),
        )
        self.dlg = self.get_dlg()
        self.view = self.get_filter_view()

    def get_dlg(self):
        dlg = ft.AlertDialog(
            title=ft.Text("Filter Settings", color=Dracula_colors.COMMENT),
            content=ft.Column(
                [
                    self.target_dropdown,
                    ft.Text("Conditions:", size=12, color=ft.Colors.GREY_700),
                    self.condition_input,  # 将 AutoComplete 放入对话框
                ],
                tight=True,
                spacing=10,
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=lambda _: setattr(dlg, "open", False)
                    or self.page.update(),
                ),
                ft.Button(
                    "Apply",
                    bgcolor=Dracula_colors.RED,
                    color=Dracula_colors.FOREGROUND,
                    on_click=self.handle_apply,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        return dlg

    def refresh_target_options(self):
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
        self.target_dropdown.options = [ft.dropdown.Option(tag) for tag in enabled_tags]
        return enabled_tags

    def handle_apply(self, e):
        if not self.target_dropdown.value or not self.condition_input.value:
            return

        # 保存本次的选择，以便下次 Add 时默认选中
        self.last_selected_target = self.target_dropdown.value

        new_data = {
            "target": self.target_dropdown.value,
            "condition": self.condition_input.value,
        }

        if self.editing_index == -1:
            self.filters_list.append(new_data)
        else:
            self.filters_list[self.editing_index] = new_data

        self.dlg.open = False
        print("Applied:", self.filters_list)
        self.render_filters()
        self.page.update()

    def open_dialog(self, index=-1):
        self.editing_index = index
        available_tags = self.refresh_target_options()

        if index == -1:
            # --- 新增模式 (Add Filter) ---
            # 优先级 1: 如果有上一次记录的选择，且该选择目前依然在启用列表中，则继续使用它
            if self.last_selected_target in available_tags:
                self.target_dropdown.value = self.last_selected_target
            # 优先级 2: 否则，如果列表不为空，默认选择第一项
            elif available_tags:
                self.target_dropdown.value = available_tags[0]
            else:
                self.target_dropdown.value = None

            self.condition_input.value = ""  # 新增时清空输入框
        else:
            # --- 编辑模式 (Long Press) ---
            item = self.filters_list[index]
            # 确保保存的值还在当前启用列表中，否则下拉框会显示空白
            self.target_dropdown.value = (
                item["target"] if item["target"] in available_tags else None
            )
            self.condition_input.value = item["condition"]

        self.dlg.open = True
        self.page.update()

    def render_filters(self):
        self.filter_items_column.controls.clear()
        for idx, item in enumerate(self.filters_list):
            self.filter_items_column.controls.append(
                ft.Dismissible(
                    content=ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.FILTER_ALT, color=Dracula_colors.COMMENT
                        ),
                        title=ft.Text(
                            f"Target: {item['target']}",
                            color=Dracula_colors.CURRENT_LINE,
                        ),
                        subtitle=ft.Text(
                            f"Condition: {item['condition']}",
                            color=Dracula_colors.COMMENT,
                        ),
                        bgcolor=Dracula_colors.BACKGROUND,
                        on_long_press=lambda _, i=idx: self.open_dialog(i),
                    ),
                    on_dismiss=lambda _, i=idx: self.remove_filter(i),
                    dismiss_direction=ft.DismissDirection.START_TO_END,
                    background=ft.Container(
                        bgcolor=Dracula_colors.RED,
                        content=ft.Text(
                            "Delete", color=Dracula_colors.FOREGROUND, weight="bold"
                        ),
                        alignment=ft.Alignment.CENTER_LEFT,
                        padding=20,
                    ),
                )
            )

    def remove_filter(self, index):
        self.filters_list.pop(index)
        self.render_filters()
        self.page.update()

    def get_filter_view(self):
        self.page.overlay.append(self.dlg)

        return ft.Column(
            controls=[
                ft.Text("Filter", size=25, weight=ft.FontWeight.BOLD),
                ft.Button(
                    "Add filtering rules",
                    icon=ft.Icons.ADD,
                    on_click=lambda _: self.open_dialog(-1),
                ),
                ft.Divider(),
                ft.Column(
                    [self.filter_items_column], scroll=ft.ScrollMode.HIDDEN, expand=True
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
