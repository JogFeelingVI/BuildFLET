# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-01 12:20:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-19 14:28:39
from .ColorTokenizer import Tokenizer, spiltfortarget
from .jackpot_core import filterFunc
from .SnackBar import get_snack_bar
from .DraculaTheme import DraculaColors
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
        self.showimg = ft.Image(
            src="filter.png",
            fit=ft.BoxFit.FIT_HEIGHT,
            width=328 * 0.45,
            height=112 * 0.45,
        )
        self.content = ft.Container(
            content=self.showimg,
            # 设置缩放动画：200毫秒，减速曲线
            animate=ft.Animation(600, ft.AnimationCurve.EASE_IN_OUT),
        )
        self.user_dir = app_data_path

    def animate_filter(self, flg: int = 1):
        # 动画逻辑：例如点击后放大并改变颜色
        scale = 1.2 if flg == 1 else 1.0
        self.showimg.scale = scale  # 改变颜色
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
        # if not self.runing:
        #     return
        # if not self.value:
        #     self.suggestions = []
        #     self.update()
        #     return
        # self.suggestions = AI_gen_sugguest_re(self.value)
        # self.update()


class Decrement_Button(ft.Container):
    """圆形按钮"""

    def __init__(
        self,
        ball_size: int = 32,
        WH: float = 0.0,
        Start_Value=1,
        Loop_Value=20,
        bgcolor=DraculaColors.RED,
        onClickOutside=None,
        onLongPressOutside=None,
    ):
        super().__init__()
        self.data = Start_Value
        self.Start_Value = Start_Value
        self.Loop_Value = Loop_Value
        self.text = f"{self.data}"
        self.ball_size = ball_size
        self.content = ft.Text(
            value=self.text,
            color=DraculaColors.FOREGROUND,
            size=self.ball_size * 0.45,
            weight=ft.FontWeight.BOLD,
        )
        self.width = self.ball_size * WH if WH > 0 else self.ball_size
        self.height = self.ball_size
        self.bgcolor = bgcolor
        self.border_radius = self.ball_size / 2
        self.alignment = ft.Alignment.CENTER
        self.shadow = ft.BoxShadow(
            spread_radius=1,
            blur_radius=4,
            color="#42000000",
            offset=ft.Offset(0, 2),
        )
        self.onClickOutside_callback = onClickOutside
        self.onLongPressOutside_callback = onLongPressOutside
        self.on_click = self.handle_click
        self.on_long_press = self.handle_long_press

    def handle_click(self, e):
        value = self.data
        value += 1
        if value > self.Loop_Value:
            value = 1
        self.data = value
        self.content.value = f"{self.data}"
        print(f"{self.data=} {self.content.value=}")
        self.update()
        if self.onClickOutside_callback:
            self.onClickOutside_callback(e)

    def handle_long_press(self, e):
        value = self.data
        value -= 2
        if value < self.Start_Value:
            value = self.Loop_Value
        self.data = value
        self.content.value = f"{self.data}"
        print(f"{self.data=} {self.content.value=}")
        self.update()
        if self.onLongPressOutside_callback:
            self.onLongPressOutside_callback(e)


class select_fang(ft.Container):
    def __init__(self, name: str = "1", size=32, on_select=None):
        super().__init__()
        self.block_size = size
        self.content = ft.Text(str(name), size=self.block_size * 0.55)
        self.width = self.block_size
        self.height = self.block_size
        self.border_radius = 5
        self.alignment = ft.Alignment.CENTER
        self.animate = ft.Animation(300, ft.AnimationCurve.DECELERATE)  # 颜色切换动画
        self.bgcolor = DraculaColors.CURRENT_LINE
        self.on_click = self.handle_click
        self.name = name
        self.selected = False
        self.on_select_callback = on_select

    def handle_click(self, e):
        self.selected = not self.selected
        self.bgcolor = (
            DraculaColors.PURPLE if self.selected else DraculaColors.CURRENT_LINE
        )
        self.update()

        if self.on_select_callback:
            self.on_select_callback(e)


class tary(ft.Row):
    def __init__(self):
        super().__init__()
        self.command = ""
        self.com_args = {0: 1, 1: 1}
        self.opet_command = ""
        self.opet_args = {0: 1, 1: 1}
        self.weic_comd = ""
        self.weic_args = []
        self.gui_size_font = 10
        self.showcommand = ft.Text(
            value="wait...", color=DraculaColors.COMMENT, size=12
        )
        self.uc_haed = ft.CupertinoSlidingSegmentedButton(
            thumb_color=DraculaColors.RED,
            selected_index=0,
            controls=[
                ft.Text("null", size=self.gui_size_font),
                ft.Text("bitX", size=self.gui_size_font),
                ft.Text("bitX,Y", size=self.gui_size_font),
                ft.Text("modX", size=self.gui_size_font),
            ],
            on_change=lambda _: self.uc_haed_change(),
        )
        self.uc_opet = ft.CupertinoSlidingSegmentedButton(
            thumb_color=DraculaColors.RED,
            selected_index=0,
            controls=[
                ft.Text(">", size=self.gui_size_font),
                ft.Text("<", size=self.gui_size_font),
                ft.Text("range", size=self.gui_size_font),
            ],
            on_change=lambda _: self.uc_opet_change(),
        )
        self.uc_weic = ft.CupertinoSlidingSegmentedButton(
            thumb_color=DraculaColors.RED,
            selected_index=0,
            controls=[
                ft.Text("#", size=self.gui_size_font),
                ft.Text("Z", size=self.gui_size_font),
                ft.Text("H", size=self.gui_size_font),
                ft.Text("J", size=self.gui_size_font),
                ft.Text("O", size=self.gui_size_font),
                ft.Text("M3", size=self.gui_size_font),
                ft.Text("W", size=self.gui_size_font),
            ],
            on_change=lambda _: self.uc_weic_change(),
        )
        self.uc_haed_row = ft.Row(
            expand=True, spacing=5, alignment=ft.MainAxisAlignment.START
        )
        self.uc_opet_row = ft.Row(
            expand=True, spacing=5, alignment=ft.MainAxisAlignment.START
        )
        self.uc_weic_row = ft.Row(
            expand=True, spacing=5, alignment=ft.MainAxisAlignment.START
        )
        # she zhi
        self.visible = False
        self.controls = [
            #
            ft.Column(
                spacing=5,
                controls=[
                    ft.Divider(),
                    ft.Row(
                        controls=[self.uc_haed],
                        expand=True,
                    ),
                    self.uc_haed_row,
                    ft.Row(
                        controls=[self.uc_opet],
                        expand=True,
                    ),
                    self.uc_opet_row,
                    ft.Row(
                        controls=[self.uc_weic],
                        expand=True,
                    ),
                    self.uc_weic_row,
                    ft.Row(
                        controls=[self.showcommand],
                        expand=True,
                    ),
                    ft.Divider(),
                ],
                expand=True,
            ),
        ]
        # self.tight = True

    def did_mount(self):
        self.uc_haed_change()
        self.uc_opet_change()
        self.uc_weic_change()
        return super().did_mount()

    def buil_command(self):
        """格式化命令行"""
        command = ""
        match self.command:
            case "bitX":
                command = f"bit{self.com_args[0]}"
            case "bitX,Y":
                command = f"bit{self.com_args[0]},{self.com_args[1]}"
            case "modX":
                command = f"mod{self.com_args[0]}"
            case _:
                pass

        command_opet = ""
        match self.opet_command:
            case ">":
                command_opet = f">{self.opet_args[0]}"
            case "<":
                command_opet = f"<{self.opet_args[0]}"
            case "range":
                command_opet = f"range {self.opet_args[0]},{self.opet_args[1]}"
            case _:
                pass

        command_weic = ""
        match self.weic_comd:
            case "--z":
                command_weic = "--z"
            case "--h":
                command_weic = "--h"
            case "--j":
                command_weic = "--j"
            case "--o":
                command_weic = "--o"
            case "--m3":
                if self.weic_args:
                    command_weic = f"--m3{''.join(map(str, self.weic_args))}"

            case "--w":
                if self.weic_args:
                    command_weic = f"--w{''.join(map(str, self.weic_args))}"

            case _:
                command_weic = ""

        all_command = [command, command_opet, command_weic]
        self.showcommand.value = " ".join(all_command)

    def loop_number_click(self, e, command, com_args):
        value = e.control.data
        self.command = command
        self.com_args[com_args] = value
        self.buil_command()

    def loop_number_long(self, e, command, com_args):
        value = e.control.data
        self.command = command
        self.com_args[com_args] = value
        self.buil_command()

    def uc_haed_change(self):
        select_index = self.uc_haed.selected_index
        flg_text = self.uc_haed.controls[select_index].value
        new_row = []
        match flg_text:
            case "null":
                self.uc_haed_row.visible = False
            case "bitX":
                new_row = [
                    ft.Text("bit"),
                    Decrement_Button(
                        ball_size=25,
                        WH=1.65,
                        bgcolor=DraculaColors.CURRENT_LINE,
                        onClickOutside=lambda e,
                        c=f"bitX",
                        ca=0: self.loop_number_click(e, c, ca),
                        onLongPressOutside=lambda e,
                        c="bitX",
                        ca=0: self.loop_number_long(e, c, ca),
                        Start_Value=1,
                        Loop_Value=20,
                    ),
                ]
            case "bitX,Y":
                new_row = [
                    ft.Text("bit"),
                    Decrement_Button(
                        ball_size=25,
                        WH=1.65,
                        bgcolor=DraculaColors.CURRENT_LINE,
                        onClickOutside=lambda e,
                        c=f"bitX,Y",
                        ca=0: self.loop_number_click(e, c, ca),
                        onLongPressOutside=lambda e,
                        c="bitX,Y",
                        ca=0: self.loop_number_long(e, c, ca),
                        Start_Value=1,
                        Loop_Value=20,
                    ),
                    Decrement_Button(
                        ball_size=25,
                        WH=1.65,
                        bgcolor=DraculaColors.COMMENT,
                        onClickOutside=lambda e,
                        c=f"bitX,Y",
                        ca=1: self.loop_number_click(e, c, ca),
                        onLongPressOutside=lambda e,
                        c="bitX,Y",
                        ca=1: self.loop_number_long(e, c, ca),
                        Start_Value=1,
                        Loop_Value=20,
                    ),
                ]
            case "modX":
                new_row = [
                    ft.Text("mod"),
                    Decrement_Button(
                        ball_size=25,
                        WH=1.65,
                        bgcolor=DraculaColors.CURRENT_LINE,
                        onClickOutside=lambda e,
                        c=f"modX",
                        ca=0: self.loop_number_click(e, c, ca),
                        onLongPressOutside=lambda e,
                        c="modX",
                        ca=0: self.loop_number_long(e, c, ca),
                        Start_Value=1,
                        Loop_Value=20,
                    ),
                ]
        self.uc_haed_row.controls = new_row
        self.uc_haed_row.visible = True
        self.command = flg_text
        self.buil_command()
        self.update()

    def select_opt_change(self, e, opet, i):
        value = e.control.data
        self.opet_command = opet
        self.opet_args[i] = value
        self.buil_command()
        # print(f"select opt {e.control.value}")

    def uc_opet_change(self):
        select_index = self.uc_opet.selected_index
        flg_text = self.uc_opet.controls[select_index].value
        new_row = []
        #! 在安卓系统下极其难用
        match flg_text:
            case ">":
                new_row = [
                    Decrement_Button(
                        ball_size=25,
                        WH=1.65,
                        bgcolor=DraculaColors.CURRENT_LINE,
                        onClickOutside=lambda e, c=f">", ca=0: self.select_opt_change(
                            e, c, ca
                        ),
                        onLongPressOutside=lambda e,
                        c=">",
                        ca=0: self.select_opt_change(e, c, ca),
                        Start_Value=1,
                        Loop_Value=160,
                    ),
                ]
            case "<":
                new_row = [
                    Decrement_Button(
                        ball_size=25,
                        WH=1.65,
                        bgcolor=DraculaColors.CURRENT_LINE,
                        onClickOutside=lambda e, c=f"<", ca=0: self.select_opt_change(
                            e, c, ca
                        ),
                        onLongPressOutside=lambda e,
                        c="<",
                        ca=0: self.select_opt_change(e, c, ca),
                        Start_Value=1,
                        Loop_Value=160,
                    ),
                ]
            case "range":
                new_row = [
                    Decrement_Button(
                        ball_size=25,
                        WH=1.65,
                        bgcolor=DraculaColors.CURRENT_LINE,
                        onClickOutside=lambda e,
                        c=f"range",
                        ca=0: self.select_opt_change(e, c, ca),
                        onLongPressOutside=lambda e,
                        c="range",
                        ca=0: self.select_opt_change(e, c, ca),
                        Start_Value=1,
                        Loop_Value=160,
                    ),
                    Decrement_Button(
                        ball_size=25,
                        WH=1.65,
                        bgcolor=DraculaColors.COMMENT,
                        onClickOutside=lambda e,
                        c=f"range",
                        ca=1: self.select_opt_change(e, c, ca),
                        onLongPressOutside=lambda e,
                        c="range",
                        ca=1: self.select_opt_change(e, c, ca),
                        Start_Value=1,
                        Loop_Value=160,
                    ),
                ]
        self.uc_opet_row.controls = new_row
        self.uc_opet_row.visible = True
        self.opet_command = flg_text
        self.buil_command()
        self.update()

    def chip_select(self, e):
        label_value = e.control.name
        isSelect = e.control.selected
        size = e.control.block_size
        if isSelect:
            if label_value not in self.weic_args:
                self.weic_args.append(label_value)
        else:
            if label_value in self.weic_args:
                self.weic_args.remove(label_value)
        self.buil_command()
        print(f"{label_value} is select {isSelect} {self.weic_args} {size=}")

    def uc_weic_change(self):
        select_index = self.uc_weic.selected_index
        flg_text = self.uc_weic.controls[select_index].value
        new_row = []
        match flg_text:
            case "Z":
                self.weic_comd = "--z"
            case "H":
                self.weic_comd = "--h"
            case "J":
                self.weic_comd = "--j"
            case "O":
                self.weic_comd = "--o"
            case "M3":
                self.weic_comd = "--m3"
                new_row = [
                    select_fang(name=i, size=25, on_select=self.chip_select)
                    for i in [0, 1, 2]
                ]
            case "W":
                self.weic_comd = "--w"
                new_row = [
                    select_fang(name=i, size=20, on_select=self.chip_select)
                    for i in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                ]
            case _:
                self.weic_comd = ""
        self.uc_weic_row.controls = new_row
        self.uc_weic_row.visible = True
        self.weic_args = []
        self.buil_command()
        self.update()
        # print(f"run uc_weic_change done.")


#
#
# New de kongjian
#
#


class FiltersList(ft.Card):
    def __init__(self, callback=None):
        super().__init__()
        self.content = self.__build_card()
        self.callback = callback
        self.automatically_save = False

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def __build_card(self):
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=400,
            border=ft.Border.all(2, DraculaColors.ORANGE),
            border_radius=10,
            content=self.__command_button(),
        )

    def addFilter(self, cmd: str):
        return

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            controls=[
                ft.Text(
                    "Various filter commands can be added to narrow down the massive pool of phone numbers."
                )
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )


class InputPad(ft.Card):
    def __init__(self, callback=None):
        super().__init__()
        self.callback = callback
        self.visible = False
        self.__FT_show = self.__load_FT_show()
        self.content = self.__build_card()

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def openPad(self):
        if not self.running:
            return
        self.visible = not self.visible
        self.update()

    def __build_card(self):
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=400,
            border=ft.Border.all(2, DraculaColors.PURPLE),
            border_radius=10,
            content=self.__Pad(),
        )

    def __Pad(self):
        """Add, Apply, Cancel"""
        return ft.Column(
            controls=[
                ft.Text(
                    "This is a test plan designed to facilitate rapid data entry for filtering projects.",
                    color=DraculaColors.PURPLE,
                ),
                self.__load_funxtarget(),
                self.__FT_show,
                ft.Divider(),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def __load_funxtarget(self):
        return ft.Row(
            controls=[
                ft.Text("Use"),
                ft.TextButton("func", icon=ft.Icons.FUNCTIONS, data="FUN", on_click=self.handle_func_click),
                ft.Text("to calculate the target"),
                ft.TextButton("all", icon=ft.Icons.FACE, data="PN"),
            ]
        )
    
    def __load_FT_show(self):
        return ft.Row(
            data="FTSHOW",
            controls=[],
            wrap=True,
            visible=False,
        )
    
    def handle_func_click(self,e):
        def function_click(k):
            if isinstance(e.control, ft.TextButton):
                e.control.content = k
                self.__FT_show.visible = False
        funcs_dc = filterFunc.getFuncName()
        
        fun_items = []
        for key, item in funcs_dc.items():
            fun_items.append(
                ft.TextButton(
                    content=f"{key}",
                    icon=ft.Icons.FUNCTIONS_SHARP,
                    on_click=lambda _, k=key: function_click(k),
                )
            )
        self.__FT_show.controls = fun_items
        self.__FT_show.visible = True
        
        

class CommandList(ft.Card):
    def __init__(self, add_callback=None):
        super().__init__()
        self.content = self.__build_card()
        self.addcallback = add_callback
        self.automatically_save = False

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def __build_card(self):
        return ft.Container(
            padding=12,
            width=float("inf"),
            # width=400,
            border=ft.Border.all(2, DraculaColors.COMMENT),
            border_radius=10,
            content=self.__command_button(),
        )

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            controls=[
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.FILTER,
                    content="Add",
                    on_click=self.handle_add,
                ),
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.SAVE,
                    content="Save",
                    # on_click=self.handle_Apply,
                ),
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.FILE_OPEN,
                    content="Open",
                    # on_click=self.handle_Cancel,
                ),
                ft.Switch(
                    expand=1,
                    label="Automatically Saved",
                    value=False,
                    active_track_color=DraculaColors.PINK,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def handle_add(self, e):
        # self.row_name_char += 1
        # new_row = self.__get_range_count(f"{chr(self.row_name_char)}")
        # temp_len = len(self.content.content.controls)
        # self.content.content.controls.insert(temp_len - 1, new_row)
        if self.running and self.addcallback:
            self.addcallback()
            if isinstance(e.control, ft.TextButton):
                if e.control.content == "Add":
                    e.control.content = "Closed"
                    e.control.icon = ft.Icons.CLOSE
                else:
                    e.control.content = "Add"
                    e.control.icon = ft.Icons.FILTER
                e.control.update()

    def handle_Cancel(self):
        self.visible = False
        self.update()


#
#
# FilterPage
#
#


class FilterPage:
    """筛选页面类"""

    def __init__(self, page: ft.Page):
        self.page = page
        self.Filters_cmd_list = FiltersList()
        self.Input_Pad = InputPad()
        self.Command_List = CommandList(add_callback=self.Input_Pad.openPad)
        # ? new control
        self.filters_list = []
        self.editing_index = -1
        self.last_selected_target = None
        self.filter_items_column = ft.Column(spacing=2)
        # --- 1. 定义 Target 下拉列表 ---
        self.pop_func = ft.PopupMenuButton(
            content=ft.Text(value="func", color=DraculaColors.GREEN, weight="bold"),
        )
        self.Fab = ft.FloatingActionButton(
            icon=ft.Icons.FILTER_LIST,
            bgcolor=DraculaColors.PINK,
            on_click=lambda _: self.open_dialog(-1),
            # opacity=0.65,
        )
        self.pop_target = ft.PopupMenuButton(
            content=ft.Text(value="all", color=DraculaColors.COMMENT, weight="bold"),
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
        self.page.session.store.set("tary", e.data)
        self.tary_row.visible = e.data
        self.condition_input.disabled = e.data
        self.condition_input.visible = not e.data

    def get_dlg(self):
        tary_value = self.page.session.store.get("tary") or False
        dlg = ft.AlertDialog(
            title=ft.Text("Filter Settings", color=DraculaColors.COMMENT),
            content=ft.Container(
                content=ft.Column(
                    controls=[
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
                                    "Conditions:", size=12, color=DraculaColors.COMMENT
                                ),
                                ft.Switch(
                                    value=tary_value,
                                    height=25,
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
                ),
                width=350,
            ),
            actions=[
                ft.TextButton("Cancel", on_click=self.close_dlg),
                ft.Button(
                    "Apply",
                    bgcolor=DraculaColors.RED,
                    color=DraculaColors.FOREGROUND,
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
            #!在这里修改
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
        tary_value = self.page.session.store.get("tary") or False
        _func = self.pop_func.content.value
        _target = self.pop_target.content.value or "all"
        _condit = (
            self.condition_input.value
            if not tary_value
            else self.tary_row.showcommand.value
        )
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
        token = Tokenizer()

        def tokenspan(text: str):
            segments = token.Segment(text)
            spans = [
                ft.TextSpan("Condition: ", style=ft.TextStyle(color=ft.Colors.WHITE))
            ]
            for text, color in segments:
                spans.append(
                    ft.TextSpan(
                        text,
                        style=ft.TextStyle(color=color if color else ft.Colors.WHITE),
                    )
                )
            return spans

        def targetspan(text: str):
            split_wc = spiltfortarget(text)
            spans = []
            for ttext, color in split_wc:
                spans.append(
                    ft.TextSpan(
                        ttext,
                        style=ft.TextStyle(color=color if color else ft.Colors.WHITE),
                    )
                )
            return spans

        self.filter_items_column.controls.clear()
        for idx, item in enumerate(self.filters_list):
            self.filter_items_column.controls.append(
                ft.Dismissible(
                    content=ft.ListTile(
                        leading=ft.Icon(
                            ft.Icons.FILTER_LIST, color=DraculaColors.ORANGE
                        ),
                        title=ft.Text(
                            spans=targetspan(
                                f"Target: {item['target']} Func: {item['func']}"
                            ),
                            # color=DraculaColors.ORANGE,
                        ),
                        #! 添加文字渲染器
                        subtitle=ft.Text(spans=tokenspan(item["condition"])),
                        # subtitle=ft.Text(
                        #     f"Condition: {item['condition']}",
                        #     color=DraculaColors.PURPLE,
                        # ),
                        # bgcolor=DraculaColors.CURRENT_LINE,
                        on_long_press=lambda _, i=idx: self.open_dialog(i),
                    ),
                    on_dismiss=lambda _, i=idx: self.remove_filter(i),
                    dismiss_direction=ft.DismissDirection.START_TO_END,
                    background=ft.Container(
                        bgcolor=DraculaColors.RED,
                        content=ft.Text(
                            "Delete", color=DraculaColors.FOREGROUND, weight="bold"
                        ),
                        alignment=ft.Alignment.CENTER_LEFT,
                        padding=20,
                        border_radius=5,
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
        # self.page.overlay.append(self.dlg)
        # user_dict_button = UserdirButton()
        # user_dict_button.setting(self.save_file, self.load_file)

        return ft.Column(
            controls=[
                ft.Image(
                    src="filter.png",
                    fit=ft.BoxFit.FIT_HEIGHT,
                    width=328 * 0.45,
                    height=112 * 0.45,
                ),
                ft.Divider(),
                self.Filters_cmd_list,
                self.Input_Pad,
                self.Command_List,
                # ft.Column(
                #     [self.filter_items_column], scroll=ft.ScrollMode.HIDDEN, expand=True
                # ),
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
