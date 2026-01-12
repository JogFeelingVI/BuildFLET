# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-01 12:20:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-12 15:11:43

from .suggestions import AI_gen_sugguest_re
from .jackpot_core import filterFunc
from .SnackBar import get_snack_bar
from .DraculaTheme import Dracula_colors
import flet as ft
import os
import json
import asyncio

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")
jackpot_filers = os.path.join(app_data_path, "jackpot_filters.dict")


class UserdirButton(ft.TextButton):
    def __init__(
        self,
    ):
        super().__init__()
        self.showtext = ft.Text(
            "Filter",
            size=25,
            weight=ft.FontWeight.BOLD,
            color=Dracula_colors.COMMENT,
        )
        self.content = ft.Container(
            content=self.showtext,
            # 设置缩放动画：200毫秒，减速曲线
            animate=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        )
        self.user_dir = app_data_path

    def animate_filter(self, flg: int = 1):
        # 动画逻辑：例如点击后放大并改变颜色
        color = Dracula_colors.PINK if flg == 1 else Dracula_colors.COMMENT
        self.showtext.color = color  # 改变颜色
        self.page.update()
        # print(f"animate is runing.{self.content.scale} {flg=}")

    def setting(self, save, load):
        self.save_funx = save
        self.load_funx = load

    def did_mount(self):
        self.ads = self.ad()
        self.page.overlay.append(self.ads)
        self.runing = True
        self.content.on_long_press = self.handle_long_press

    def will_unmount(self):
        self.runing = False

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

    def handle_long_press(self):
        self.animate_filter(1)
        self.page.run_task(self.select_dir)
        self.ads.open = True
        self.page.update()

    def ad(self):
        return ft.AlertDialog(
            title=ft.Text("Filter settings saved"),
            content=ft.Text("Do you need to save or load jackpot_filters.dict?"),
            actions=[
                ft.TextButton("Save", on_click=self.handle_save),
                ft.TextButton(
                    "Load",
                    on_click=self.handle_load,
                ),
            ],
            on_dismiss=lambda _: self.animate_filter(0),
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def handle_save(self):
        # print(f"{self.user_dir=}")
        try:
            if self.save_funx:
                self.save_funx(self.user_dir)
        finally:
            self.ads.open = False
            self.page.update()

    def handle_load(self):
        # print(f"{self.user_dir=}")
        try:
            if self.load_funx:
                self.load_funx(self.user_dir)
        finally:
            self.ads.open = False
            self.page.update()


class AI_Auto_input(ft.TextField):
    def __init__(self):
        super().__init__()
        self.border = ft.InputBorder.UNDERLINE
        self.expand = True
        self.on_change = self.on_change_input

    def did_mount(self):
        self.runing = True
        return super().did_mount()

    def will_unmount(self):
        self.runing = False
        return super().will_unmount()

    def on_change_input(self, e):
        # print(f"uset input: {self.value}")
        return
        self.page.run_task(self.ai_sugguest_set)

    async def ai_sugguest_set(self):
        """已经废弃不可食用"""
        await asyncio.sleep(0.3)
        if not self.runing:
            return
        if not self.value:
            self.suggestions = []
            self.update()
            return
        self.suggestions = AI_gen_sugguest_re(self.value)
        self.update()


class tary(ft.Row):
    def __init__(self):
        super().__init__()
        self.command = ''
        self.com_args = {0:1,1:1}
        self.showcommand = ft.Text(value="wait...",color=Dracula_colors.COMMENT,size=12)
        self.uc_haed = ft.CupertinoSlidingSegmentedButton(
            thumb_color=Dracula_colors.PURPLE,
            selected_index=0,
            controls=[
                ft.Text("null"),
                ft.Text("bitX"),
                ft.Text("bitX,Y"),
                ft.Text("modX"),
            ],
            on_change=lambda _: self.uc_haed_change(),
        )
        self.uc_opet = ft.CupertinoSlidingSegmentedButton(
            thumb_color=Dracula_colors.PURPLE,
            selected_index=0,
            controls=[ft.Text(">"), ft.Text("<"), ft.Text("range")],
            on_change=lambda _: self.uc_haed_change(),
        )
        self.uc_haed_row = ft.Row(tight=True,align=ft.Alignment.CENTER_LEFT, spacing=5)
        # she zhi
        self.visible = False
        self.controls = [
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[self.uc_haed],
                        tight=True,
                        align=ft.Alignment.CENTER_LEFT,
                    ),
                    self.uc_haed_row,
                    ft.Row(
                        controls=[self.showcommand],
                        tight=True,
                        align=ft.Alignment.CENTER_LEFT,
                    ),
                ],
                tight=True,
                align=ft.Alignment.CENTER_LEFT,
            ),
        ]
        self.tight = True
        self.align = ft.Alignment.CENTER_LEFT

    def did_mount(self):
        self.uc_haed_change()
        return super().did_mount()
    
    def buil_command(self):
        match self.command:
            case "bitX":
                self.showcommand.value =f'bit{self.com_args[0]}'
            case "bitX,Y":
                self.showcommand.value =f'bit{self.com_args[0]},{self.com_args[1]}'
            case "modX":
                self.showcommand.value =f'mod{self.com_args[0]}'
            case _:
                self.showcommand.value =f'mod{self.com_args[0]}'
                

    def loop_number_click(self,e,command,com_args):
        value = e.control.data
        value += 1
        if value > 20:
            value = 1
        e.control.data = value
        e.control.content = f"{e.control.data}"
        self.command = command
        self.com_args[com_args] = value
        self.buil_command()

   
    def loop_number_long(self,e,command,com_args):
        value = e.control.data
        value -= 2
        if value < 1:
            value = 20
        e.control.data = value
        e.control.content = f"{e.control.data}"
        self.command = command
        self.com_args[com_args] = value
        self.buil_command()
        
    def reload_command(self):
        self.command = ''
        self.com_args = {0:1,1:1}
        self.showcommand.value = "wait..."
        

    def uc_haed_change(self):
        select_index = self.uc_haed.selected_index
        flg_text = self.uc_haed.controls[select_index].value
        match flg_text:
            case "null":
                self.uc_haed_row.visible = False
            case "bitX":
                new_row = [
                    ft.Text("bit"),
                    ft.Button(
                        content="1",
                        data=1,
                        style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=5),
                        bgcolor=Dracula_colors.CURRENT_LINE,
                        on_click=lambda e,c=f"bitX",ca=0:self.loop_number_click(e,c,ca),
                        on_long_press=lambda e,c="bitX",ca=0:self.loop_number_long(e,c,ca),
                    ),
                ]
                self.uc_haed_row.controls = new_row
                self.uc_haed_row.visible = True
            case "bitX,Y":
                new_row = [
                    ft.Text("bit"),
                    ft.Button(
                        content="1",
                        data=1,
                        style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=5),
                        bgcolor=Dracula_colors.CURRENT_LINE,
                        on_click=lambda e,c="bitX,Y",ca=0:self.loop_number_click(e,c,ca),
                        on_long_press=lambda e,c="bitX,Y",ca=0:self.loop_number_long(e,c,ca),
                    ),
                    ft.Button(
                        content="1",
                        data=1,
                        style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=5),
                        bgcolor=Dracula_colors.CURRENT_LINE,
                        on_click=lambda e,c="bitX,Y",ca=1:self.loop_number_click(e,c,ca),
                        on_long_press=lambda e,c="bitX,Y",ca=1:self.loop_number_long(e,c,ca),
                    ),
                ]
                self.uc_haed_row.controls = new_row
                self.uc_haed_row.visible = True
            case "modX":
                new_row = [
                    ft.Text("mod"),
                    ft.Button(
                        content="1",
                        data=1,
                        style=ft.ButtonStyle(shape=ft.CircleBorder(), padding=5),
                        bgcolor=Dracula_colors.CURRENT_LINE,
                        on_click=lambda e,c="modX",ca=0:self.loop_number_click(e,c,ca),
                        on_long_press=lambda e,c="modX",ca=0:self.loop_number_long(e,c,ca),
                    ),
                ]
                self.uc_haed_row.controls = new_row
                self.uc_haed_row.visible = True
        self.reload_command()
        self.update()


class FilterPage:
    """筛选页面类"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.filters_list = []
        self.editing_index = -1
        self.last_selected_target = None
        self.filter_items_column = ft.Column(spacing=2)
        # --- 1. 定义 Target 下拉列表 ---
        self.pop_func = ft.PopupMenuButton(
            content=ft.Text(value="func", color=Dracula_colors.GREEN, weight="bold"),
        )
        self.Fab = ft.FloatingActionButton(
            icon=ft.Icons.FILTER,
            bgcolor=Dracula_colors.PINK,
            on_click=lambda _: self.open_dialog(-1),
            # opacity=0.65,
        )
        self.pop_target = ft.PopupMenuButton(
            content=ft.Text(value="all", color=Dracula_colors.COMMENT, weight="bold"),
        )
        self.tary_row = tary()
        self.condition_input = AI_Auto_input()
        self.input_row = ft.Row(
            controls=[
                self.condition_input,
            ],
            align=ft.Alignment.CENTER_LEFT,
            tight=True,
        )
        self.dlg = self.get_dlg()
        self.view = self.get_filter_view()

    def close_dlg(self, e):
        self.dlg.open = False
        self.page.update()

    def tary_change(self, e):
        self.tary_row.visible = e.data
        self.condition_input.disabled = e.data
        self.condition_input.visible = not e.data

    def get_dlg(self):
        dlg = ft.AlertDialog(
            title=ft.Text("Filter Settings", color=Dracula_colors.COMMENT),
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            controls=[
                                ft.Text("Select Fun:"),
                                self.pop_func,
                                ft.Text("Target:"),
                                self.pop_target,
                            ],
                            tight=True,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    "Conditions:", size=12, color=Dracula_colors.COMMENT
                                ),
                                ft.Switch(
                                    height=20,
                                    value=False,
                                    on_change=self.tary_change,
                                ),
                            ],
                            align=ft.Alignment.CENTER_LEFT,
                            tight=True,
                        ),
                        self.tary_row,
                        self.input_row,
                    ],
                    tight=True,
                    spacing=10,
                ),
                width=300,  # 锁定宽度防止抖动
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dlg),
                ft.Button(
                    "Apply",
                    bgcolor=Dracula_colors.RED,
                    color=Dracula_colors.FOREGROUND,
                    on_click=self.handle_apply,
                ),
            ],
        )
        return dlg

    def handle_func_click(self, name: str):
        self.pop_func.content.value = name

    def handle_target_click(self, name: str):
        self.pop_target.content.value = name

    def refresh_target_options(self):
        try:
            global jackpot_seting
            enabled_tags = ["all"]
            if not os.path.exists(jackpot_seting):
                return
            with open(jackpot_seting, "r", encoding="utf-8") as f:
                data = json.load(f)
                random_data = data.get("randomData", {})
                for key, content in random_data.items():
                    if isinstance(content, dict) and content.get("enabled") is True:
                        enabled_tags.append(key)
            if len(enabled_tags) == 1:
                return
            new_pop_items = []
            for key in enabled_tags:
                new_pop_items.append(
                    ft.PopupMenuItem(
                        content=f"{key}",
                        on_click=lambda e, k=key: self.handle_target_click(k),
                    )
                )
            self.pop_target.items = new_pop_items
        except Exception:
            self.page.show_dialog(
                get_snack_bar("refresh target options error.", "error")
            )
        return enabled_tags

    def refresh_func_options(self):
        self.funcs_dict = filterFunc.getFuncName()
        new_pop_items = []
        for key, item in self.funcs_dict.items():
            new_pop_items.append(
                ft.PopupMenuItem(
                    content=f"{key}",
                    on_click=lambda e, k=key: self.handle_func_click(k),
                )
            )
        self.pop_func.items = new_pop_items
        return list(self.funcs_dict.keys())

    def handle_apply(self, e):
        _func = self.pop_func.content.value
        _target = self.pop_target.content.value or "all"
        _condit = self.condition_input.value
        if _func == "func" or _condit == "":
            return

        # 保存本次的选择，以便下次 Add 时默认选中
        self.last_selected_target = _target

        new_data = {
            "func": _func,
            "target": _target,
            "condition": _condit,
        }

        if self.editing_index == -1:
            self.filters_list.append(new_data)
        else:
            self.filters_list[self.editing_index] = new_data

        self.dlg.open = False
        self.render_filters()
        self.page.session.store.set("filters", self.filters_list)
        self.page.update()

    def open_dialog(self, index=-1):
        self.editing_index = index
        available_tags = self.refresh_target_options()
        available_func = self.refresh_func_options()

        if index == -1:
            # --- 新增模式 (Add Filter) ---
            # 优先级 1: 如果有上一次记录的选择，且该选择目前依然在启用列表中，则继续使用它
            if self.last_selected_target in available_tags:
                self.pop_target.content.value = self.last_selected_target
            # 优先级 2: 否则，如果列表不为空，默认选择第一项
            elif available_tags:
                self.pop_target.content.value = available_tags[0]
            else:
                self.pop_target.content.value = "all"

            self.condition_input.value = ""  # 新增时清空输入框
        else:
            # --- 编辑模式 (Long Press) ---
            item = self.filters_list[index]
            # 确保保存的值还在当前启用列表中，否则下拉框会显示空白
            self.pop_target.content.value = (
                item["target"] if item["target"] in available_tags else None
            )
            self.pop_func.content.value = (
                item["func"] if item["func"] in available_func else None
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
                            ft.Icons.FILTER_ALT, color=Dracula_colors.ORANGE
                        ),
                        title=ft.Text(
                            f"Target: {item['target']} Func: {item['func']}",
                            color=Dracula_colors.ORANGE,
                        ),
                        subtitle=ft.Text(
                            f"Condition: {item['condition']}",
                            color=Dracula_colors.PURPLE,
                        ),
                        # bgcolor=Dracula_colors.CURRENT_LINE,
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
        self.page.session.store.set("filters", self.filters_list)
        self.page.update()

    def save_file(self, user_dirs: str):
        file_path = os.path.join(user_dirs, "jackpot_filters.dict")
        with open(file_path, "w", encoding="utf-8") as f:
            for item in self.filters_list:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        self.page.show_dialog(get_snack_bar(f"{file_path} saved successfully."))

    def load_file(self, user_dirs: str):
        file_path = os.path.join(user_dirs, "jackpot_filters.dict")
        if not os.path.isfile(file_path):
            return
        filters_list = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # 去掉行尾换行符并确保行不为空
                line = line.strip()
                if line:
                    # 将每一行的 JSON 字符串转回字典对象
                    item = json.loads(line)
                    filters_list.append(item)
        if not filters_list:
            return
        self.filters_list = filters_list
        self.page.session.store.set("filters", self.filters_list)
        self.render_filters()
        self.page.update()

    def get_filter_view(self):
        self.page.overlay.append(self.dlg)
        user_dict_button = UserdirButton()
        user_dict_button.setting(self.save_file, self.load_file)

        return ft.Column(
            controls=[
                user_dict_button,
                # ft.Button(
                #     "Add filtering rules",
                #     icon=ft.Icons.ADD,
                #     on_click=lambda _: self.open_dialog(-1),
                # ),
                ft.Divider(),
                ft.Column(
                    [self.filter_items_column], scroll=ft.ScrollMode.HIDDEN, expand=True
                ),
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
