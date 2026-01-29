# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-01 12:20:24
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-29 03:07:10

from .ColorTokenizer import Tokenizer, spiltfortarget
from .jackpot_core import filterFunc
from .SnackBar import get_snack_bar
from .DraculaTheme import DraculaColors
from .jackpot_core import randomData
from .loger import loger as logr
import flet as ft
import os
import json
import asyncio
import hashlib

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")


_ = r"""_|_|_|_|  _|  _|    _|                                    _|        _|              _|      
_|            _|  _|_|_|_|    _|_|    _|  _|_|    _|_|_|  _|              _|_|_|  _|_|_|_|  
_|_|_|    _|  _|    _|      _|_|_|_|  _|_|      _|_|      _|        _|  _|_|        _|      
_|        _|  _|    _|      _|        _|            _|_|  _|        _|      _|_|    _|      
_|        _|  _|      _|_|    _|_|_|  _|        _|_|_|    _|_|_|_|  _|  _|_|_|        _|_|  """


class FiltersList(ft.Card):
    def __init__(
        self,
    ):
        super().__init__()
        self.content = self.__build_card()
        self.editItemCallback = None
        self.add_closed_stat = None
        self.filtersAll_change = "none"  # add none del edit
        self.filtersAll = []
        self.filterSeed = set()
        

    def setting_edit_Callback(self, edit_item_callback=None):
        self.editItemCallback = edit_item_callback

    def setting_command_stat(self, add_closed_stat: None):
        self.add_closed_stat = add_closed_stat

    def givefilterall(self):
        return self.filtersAll

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

    def targetspan(self, text: str):
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

    def tokenspan(self, text: str):
        segments = Tokenizer().Segment(text)
        spans = []
        for text, color in segments:
            spans.append(
                ft.TextSpan(
                    text,
                    style=ft.TextStyle(color=color if color else ft.Colors.WHITE),
                )
            )
        return spans

    def addFilter(self, scriptd: dict):
        _scd = scriptd.copy()
        if "" in _scd.values():
            logr.info(f"add filter error {_scd}")
            return
        if not isinstance(self.content.content, ft.Row):
            return

        # hash 确认
        def hashcode(scr: dict, cmd: str = "is"):
            scr_obj = f"{scr['func']}{scr['target']}{scr['condition']}"
            scr_hash = hashlib.sha256(scr_obj.encode("utf-8"))
            match cmd.lower().strip():
                case "is":
                    if scr_hash.hexdigest() not in self.filterSeed:
                        self.filterSeed.add(f"{scr_hash.hexdigest()}")
                        return True
                    else:
                        return False
                case "del":
                    if scr_hash.hexdigest() in self.filterSeed:
                        self.filterSeed.remove(scr_hash.hexdigest())
                case _:
                    pass

        if hashcode(_scd, "is") == False:
            return

        controls = self.content.content.controls

        def deleteForE(e):
            if not isinstance(e.control, ft.Chip):
                return
            e_chip = e.control
            e_script = e.control.data
            hashcode(e_script, "del")
            controls.remove(e_chip)
            self.filtersAll.remove(e_script)
            self.filtersAll_change = "del"

        def editForE(e):
            if not isinstance(e.control, ft.Chip):
                return
            e_chip = e.control
            e_script = e.control.data
            # logr.info(f"edit {e_chip.data}")
            hashcode(e_script, "del")
            controls.remove(e_chip)
            self.filtersAll.remove(e_script)
            if self.editItemCallback:
                self.editItemCallback(e_script)
            if self.add_closed_stat:
                self.add_closed_stat()
            e_chip.update()
            self.filtersAll_change = "edit"

        self.filtersAll.append(_scd)
        controls.append(
            ft.Chip(
                data=_scd,
                label=ft.Column(
                    spacing=0,
                    controls=[
                        ft.Text(
                            spans=self.targetspan(f"{_scd['func']} {_scd['target']}"),
                            size=14,
                        ),
                        ft.Text(spans=self.tokenspan(f"{_scd['condition']}"), size=14),
                    ],
                ),
                # leading=ft.Icon(ft.Icons.FILTER_ALT),
                label_padding=ft.Padding.only(left=3),
                padding=3,
                delete_icon=ft.Container(
                    content=ft.Icon(
                        ft.Icons.DELETE_FOREVER,
                        color=DraculaColors.RED,
                        size=20,
                        margin=0,
                    ),
                    margin=ft.Margin.all(0),
                    padding=0,
                ),
                # delete_icon_color=DraculaColors.RED,
                on_delete=deleteForE,
                on_click=editForE,
            )
        )
        self.filtersAll_change = "add"
        self.content.content.update()
        self.filter_data_task()

    def filter_data_task(self):
        # self.page.session.store.set("filters", fiter_data)
        self.page.session.store.set("filters", self.filtersAll)

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            wrap=True,
            controls=[
                ft.Switch(
                    thumb_color={
                        ft.ControlState.DEFAULT: DraculaColors.FOREGROUND,
                        ft.ControlState.SELECTED: DraculaColors.PINK,
                    },
                    track_color={
                        ft.ControlState.DEFAULT: DraculaColors.BACKGROUND,
                        ft.ControlState.SELECTED: DraculaColors.BACKGROUND,
                    },
                    track_outline_color=DraculaColors.PINK,
                    value=False,
                    on_change=self.handle_switch,
                    tooltip=ft.Tooltip(
                        message="It saves automatically every 20 seconds."
                    ),
                ),
                # "Various filter commands can be added to narrow down the massive pool of phone numbers."
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
        )
        
    def clear_all(self):
        """清空 filter 设置"""
        row = self.content.content
        if not isinstance(row, ft.Row):
            return
        rows = [x for x in row.controls if isinstance(x, ft.Switch)]
        row.controls = rows
        self.filtersAll.clear()
        self.filterSeed.clear()
        row.update()
            
    def handle_switch(self, e):
        switch = e.control
        if not isinstance(switch, ft.Switch):
            return
        if not switch.value:
            switch.badge = None
            return
        self.page.run_task(self.auto_save, switch, 10)

    async def auto_save(self, sw: ft.Switch, time: int = 10):
        _time = time
        while _time != 0:
            await asyncio.sleep(2)
            _time -= 1
            sw.badge = f"{_time}"
            if self.filtersAll:
                self.page.run_task(self.saveTodict)
            if _time == 0:
                _time = time
            if not sw.value:
                sw.badge = None
                break
            sw.update()

    async def saveTodict(self):
        if self.filtersAll_change == "none":
            return
        self.page.session.store.set("filters", self.filtersAll)
        stored_id = await ft.SharedPreferences().get("stored_id")
        if not stored_id:
            logr.error("ID not found.")
            return
        try:
            with open(stored_id, "w", encoding="utf-8") as f:
                for item in self.filtersAll:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            logr.info(f"saveTodict is run.")
            self.filtersAll_change = "none"
        except Exception as ex:
            logr.info(f"Auto Save error {ex}")


class InputPad(ft.Card):
    def __init__(self):
        super().__init__()
        self.applycallback = None
        self.visible = False
        self.__FT_show = self.__load_FT_show()
        self.content = self.__build_card()
        self.funcs_dc = {}
        self.target_pn = ["all"]
        self.pad_data = {"func": "", "target": "", "condition": ""}

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def settingApplyCallback(self, applycallback=None):
        self.applycallback = applycallback

    def openPad(self):
        """新增加模式"""
        if not self.running:
            return
        self.visible = not self.visible
        self.update()

    def editePad(self, script: dict):
        """编辑模式"""
        func_target: list = self.content.content.controls
        for item in func_target:
            match item.data:
                case "__load_funxtarget":
                    if not isinstance(item, ft.Row):
                        continue
                    if not isinstance(item.controls[0], ft.Text):
                        continue
                    text_spans = item.controls[0].spans
                    text_spans[1].text = script["func"]
                    text_spans[3].text = script["target"]
                    self.pad_data["func"] = script["func"]
                    self.pad_data["target"] = script["target"]
                    self.pad_data["condition"] = script["condition"]
                    # logr.info(f"editPad {self.pad_data=} {text_spans[1].text=}")
                case "__command_input":
                    if not isinstance(item, ft.TextField):
                        continue
                    item.value = script["condition"]
                case "__apply_text":
                    # logr.info('__apply_text.')
                    if not isinstance(item, ft.Row):
                        continue
                    if not isinstance(item.controls[0], ft.Chip):
                        continue
                    item.controls[0].label = "Click to finish editing."
                case _:
                    pass
        self.visible = True
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
            data="__Pad",
            controls=[
                ft.Text(
                    "This is a test plan designed to facilitate rapid data entry for filtering projects.",
                    color=DraculaColors.PURPLE,
                ),
                self.__load_funxtarget(),
                self.__FT_show,
                ft.Divider(),
                self.__command_input(),
                ft.Divider(),
                self.__apply_text(),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def __apply_text(self):
        """Click "Apply" to add the filter."""
        return ft.Row(
            data="__apply_text",
            controls=[
                ft.Chip(
                    label="Click to add a filter.",
                    label_text_style=ft.TextStyle(color=DraculaColors.BACKGROUND),
                    bgcolor=DraculaColors.GREEN,
                    on_click=self.handle_apply_click,
                ),
            ],
        )

    def __command_input(self):
        def input_change(e):
            if not isinstance(e.control, ft.TextField):
                return
            self.pad_data["condition"] = f"{e.control.value}".strip()

        return ft.TextField(
            data="__command_input",
            label="Execute the script",
            hint_text="exp: bit1,2 range 1,15 --z",
            expand=1,
            border=ft.InputBorder.UNDERLINE,
            on_change=input_change,
        )

    def __load_funxtarget(self):
        """Use "avg" to calculate the target "pa"."""
        def_text_style = ft.TextStyle(size=14, color=DraculaColors.COMMENT)
        fun_text_style = ft.TextStyle(size=14, color=DraculaColors.ORANGE)
        tar_text_style = ft.TextStyle(size=14, color=DraculaColors.GREEN)
        return ft.Row(
            data="__load_funxtarget",
            controls=[
                ft.Text(
                    spans=[
                        ft.TextSpan(
                            "use ",
                            style=def_text_style,
                        ),
                        ft.TextSpan(
                            "*fun*",
                            style=fun_text_style,
                            on_click=self.handle_func_click,
                        ),
                        ft.TextSpan(" to calculate the target ", style=def_text_style),
                        ft.TextSpan(
                            "*pn*",
                            style=tar_text_style,
                            on_click=self.handle_pn_click,
                        ),
                    ]
                ),
            ],
        )

    def __load_FT_show(self):
        return ft.Row(
            data="__load_FT_show",
            controls=[],
            wrap=True,
            spacing=2,
            run_spacing=2,
            visible=False,
        )

    def handle_apply_click(self, e):
        if "" in self.pad_data.values():
            return
        if not isinstance(e.control, ft.Chip):
            return
        e.control.label = "Click to add a filter."
        # logr.info(f'handle_apply_click {self.pad_data=}')
        if self.applycallback:
            self.applycallback(scriptd=self.pad_data)
        e.control.update()

    def handle_func_click(self, e):
        def function_click(k):
            if isinstance(e.control, ft.TextSpan):
                e.control.text = f"{k}"
                e.control.data = k
                self.__FT_show.visible = False
                self.pad_data["func"] = f"{k}".strip()

        if self.funcs_dc.__len__() == 0:
            self.funcs_dc = dict(sorted(filterFunc.getFuncName().items()))

        fun_items = []
        for key, item in self.funcs_dc.items():
            fun_items.append(
                ft.Chip(
                    padding=2,
                    label=f"{key}",
                    data=key,
                    leading=ft.Icon(ft.Icons.FUNCTIONS),
                    on_click=lambda _, k=key: function_click(k),
                )
            )
        self.__FT_show.controls = fun_items
        self.__FT_show.visible = True

    def handle_pn_click(self, e):
        def function_click(k):
            if isinstance(e.control, ft.TextSpan):
                e.control.text = f"{k}"
                e.control.data = k
                self.__FT_show.visible = False
                self.pad_data["target"] = f"{k}".strip()

        try:
            global jackpot_seting
            if not os.path.exists(jackpot_seting):
                return
            with open(jackpot_seting, "r", encoding="utf-8") as f:
                data = json.load(f)
                random_data = data.get("randomData", {})
                self.target_pn = ["all"]
                for key, content in random_data.items():
                    if isinstance(content, dict) and content.get("enabled") is True:
                        self.target_pn.append(key)
            # ? target_pn 已经装载执行下面
            target_pn_items = []
            for key in self.target_pn:
                target_pn_items.append(
                    ft.Chip(
                        padding=2,
                        label=f"{key}",
                        data=key,
                        leading=ft.Icon(ft.Icons.FACE),
                        on_click=lambda _, k=key: function_click(k),
                    )
                )
            self.__FT_show.controls = target_pn_items
            self.__FT_show.visible = True
        except Exception as e:
            pass

# commandlist
#
#
# 
#
#
#

class CommandList(ft.Card):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()
        self.addcallback = None
        self.filterAddItem = None
        self.give_data = None
        self.filter_clear_all = None
        self.automatically_save = False
        self.fileMg = ft.FilePicker(on_upload=self.handle_upload)

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False
        
    def setting_filter_clear_all(self, cleal_all:None):
        self.filter_clear_all = cleal_all

    def setting_give_data(self, give_data: None):
        self.give_data = give_data

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
                    key="add_close",
                    icon=ft.Icons.ADD_CARD,
                    content="Add",
                    on_click=self.handle_add,
                ),
                ft.TextButton(
                    icon=ft.Icons.FILE_OPEN,
                    content="Open",
                    on_click=self.handle_Open,
                ),
                ft.TextButton(
                    icon=ft.Icons.FILE_DOWNLOAD,
                    content="Save",
                    on_click=self.handle_Save,
                ),
                ft.TextButton(
                    icon=ft.Icons.FILE_UPLOAD,
                    content="Load",
                    on_click=self.handle_Load,
                )
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
        )

    def setting_edit_stat_open(self):
        # e.control.content = "Add"
        # e.control.icon = ft.Icons.FILTER
        row_controls = self.content.content.controls
        # 查找 key 为 "btn_add" 的控件
        add_close = next((c for c in row_controls if c.key == "add_close"), None)
        if not isinstance(add_close, ft.TextButton):
            return
        add_close.content = "Closed"
        add_close.icon = ft.Icons.CLOSE

    def setting_add_callback(self, addCallBack=None):
        self.addcallback = addCallBack

    def setting_filte_add_item(self, filterAddItem=None):
        self.filterAddItem = filterAddItem

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

    async def handle_Save(self, e):
        stored_id = await ft.SharedPreferences().get("stored_id")
        if not stored_id:
            logr.error("ID not found.")
            return
        with open(stored_id, "r", encoding="utf-8") as f:
            content = f.read()
            content_bytes = content.encode("utf-8")
            save_path = await self.fileMg.save_file(
                dialog_title="Save as jackpot_filters.dict file.",
                allowed_extensions=["dict"],
                file_name="jackpot_filters.dict",
                src_bytes=content_bytes,
            )
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(content_bytes)
            logr.info(f"Filter saved successfully. {save_path}")

    async def handle_Open(self, e):
        stored_id = await ft.SharedPreferences().get("stored_id")
        if not stored_id:
            logr.error("ID not found.")
            return

        fiter_data = []
        if self.filter_clear_all:
            self.filter_clear_all()
        with open(stored_id, "r", encoding="utf-8") as f:
            for line in f:
                # 去掉行尾换行符并确保行不为空
                line = line.strip()
                if line:
                    # 将每一行的 JSON 字符串转回字典对象
                    item = json.loads(line)
                    fiter_data.append(item)
                    if self.filterAddItem:
                        self.filterAddItem(item)
        self.page.session.store.set("filters", fiter_data)
        logr.info(f"Reading complete. {len(fiter_data)}")

    def handle_upload(self, e):
        logr.info(f"handle upload {e}")
        if e.progress==1.0 and e.error==None:
            filepath = os.path.join(app_temp_path, e.file_name)
            logr.info(f'upload Fullpath {filepath}')
            fiter_data = []
            if self.filter_clear_all:
                self.filter_clear_all()
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    # 去掉行尾换行符并确保行不为空
                    line = line.strip()
                    if line:
                        # 将每一行的 JSON 字符串转回字典对象
                        item = json.loads(line)
                        fiter_data.append(item)
                        if self.filterAddItem:
                            self.filterAddItem(item)
            self.page.session.store.set("filters", fiter_data)
            logr.info(f"Reading complete. {len(fiter_data)}")

    async def handle_Load(self, e):
        pick_result = await self.fileMg.pick_files(
            dialog_title="",
            allow_multiple=False,
            allowed_extensions=["dict"],
        )
        if not pick_result:
            return
        logr.info(f"selsect file: {pick_result}")
        if self.page.web:
            uplpads = [
                ft.FilePickerUploadFile(
                    self.page.get_upload_url(pick_result[0].name, 600),
                    "PUT",
                    None,
                    pick_result[0].name,
                )
            ]
            await self.fileMg.upload(uplpads)
        else:
            fiter_data = []
            if self.filter_clear_all:
                self.filter_clear_all()
            with open(pick_result[0].path, "r", encoding="utf-8") as r:
                for line in r:
                    # 去掉行尾换行符并确保行不为空
                    line = line.strip()
                    if line:
                        # 将每一行的 JSON 字符串转回字典对象
                        item = json.loads(line)
                        fiter_data.append(item)
                        if self.filterAddItem:
                            self.filterAddItem(item)
            self.page.session.store.set("filters", fiter_data)
            logr.info(f"Reading complete. {len(fiter_data)}")


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
        self.Command_List = CommandList()

        self.Input_Pad.settingApplyCallback(
            applycallback=self.Filters_cmd_list.addFilter
        )
        self.Command_List.setting_add_callback(addCallBack=self.Input_Pad.openPad)
        self.Command_List.setting_give_data(
            give_data=self.Filters_cmd_list.givefilterall
        )
        self.Command_List.setting_filte_add_item(
            filterAddItem=self.Filters_cmd_list.addFilter
        )
        self.Command_List.setting_filter_clear_all(self.Filters_cmd_list.clear_all)
        self.Filters_cmd_list.setting_edit_Callback(self.Input_Pad.editePad)
        self.Filters_cmd_list.setting_command_stat(
            add_closed_stat=self.Command_List.setting_edit_stat_open
        )
        # ? new control
        self.view = self.get_filter_view()

    def get_filter_view(self):
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
