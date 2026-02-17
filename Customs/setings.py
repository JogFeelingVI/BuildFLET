# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-17 15:13:06

from .DraculaTheme import DraculaColors, RandColor
from .jackpot_core import randomData
from dataclasses import dataclass, field
from .loger import logr
import flet as ft
import json
import os
import re
import asyncio
import pathlib
import random

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")

# region Lotter_Data
Lotter_Data = {
    "🔴双色球": {
        "description": "🇨🇳百万富翁缔造者",
        "SA": [1, 33],
        "SB": [1, 16],
        "SA_K": 6,
        "SB_K": 1,
    },
    "⚪快乐8": {
        "description": "🇨🇳你的快乐就是他的快乐",
        "PA": [1, 80],
        "PA_K": 10,
    },
    "✨超级大乐透": {
        "description": "🇨🇳体育大乐透",
        "PA": [1, 35],
        "PB": [1, 12],
        "PA_K": 5,
        "PB_K": 2,
    },
    "🇨🇳排列3/5": {
        "description": "🇨🇳体育排列3/5",
        "PA": [0, 9],
        "PB": [0, 9],
        "PC": [0, 9],
        "PD": [0, 9],
        "PE": [0, 9],
        "PA_K": 1,
        "PB_K": 1,
        "PC_K": 1,
        "PD_K": 1,
        "PE_K": 1,
    },
    "✨七星彩": {
        "description": "🇨🇳体育七星彩",
        "PA": [0, 9],
        "PB": [0, 9],
        "PC": [0, 9],
        "PD": [0, 9],
        "PE": [0, 9],
        "PF": [0, 9],
        "PG": [0, 14],
        "PA_K": 1,
        "PB_K": 1,
        "PC_K": 1,
        "PD_K": 1,
        "PE_K": 1,
        "PF_K": 1,
        "PG_K": 1,
    },
    "🇺🇸Powerball": {
        "description": "🇺🇸USA Powerball",
        "PA": [1, 69],
        "PB": [1, 26],
        "PA_K": 5,
        "PB_K": 1,
    },
    "🇹🇼威力彩": {
        "description": "🇺🇸台湾省销售最好的彩票",
        "PA": [1, 38],
        "PB": [1, 8],
        "PA_K": 6,
        "PB_K": 1,
    },
}
# endregion


# region input_user_rule
class input_user_rule(ft.Container):
    def __init__(self):
        super().__init__()
        self.visible = False
        self.bgX = RandColor()
        self.content = self.__build_card()
        self.render_filters = None
        self.row_name_char = 65
        self.templejson = {
            "randomData": {
                "note": "🇨🇳体育排列3/5",
                "PA": {"enabled": True, "range_start": 0, "range_end": 9, "count": 1},
            }
        }
        self.width = float("inf")
        self.border = ft.Border.all(1, ft.Colors.with_opacity(0.5, self.bgX))
        self.bgcolor = ft.Colors.with_opacity(0.6, self.bgX)
        self.border_radius = 10

    def setting_render_filters(self, render_filters=None):
        self.render_filters = render_filters

    def did_mount(self):
        self.running = True

    def will_unmount(self):
        self.running = False

    def openCard(self):
        self.visible = True
        self.update()

    def __command_button(self):
        """Add, Apply, Cancel"""
        return ft.Row(
            controls=[
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.ADD_BOX,
                    content="Add",
                    on_click=self.handle_add,
                ),
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.WINDOW,
                    style=ft.ButtonStyle(
                        bgcolor=self.bgX,
                        color=DraculaColors.BACKGROUND,
                        shape=ft.RoundedRectangleBorder(radius=5),
                    ),
                    content="Apply",
                    on_click=self.handle_Apply,
                ),
                ft.TextButton(
                    expand=1,
                    icon=ft.Icons.CANCEL,
                    content="Cancel",
                    on_click=self.handle_Cancel,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

    def __get_note(self):
        return ft.TextField(
            label="Note",
            hint_text="Rule Settings Instructions",
            expand=1,
            border=ft.InputBorder.UNDERLINE,
        )

    def __get_range_count(self, name="a"):
        name = name.upper()
        return ft.Row(
            controls=[
                ft.TextField(
                    label=f"P{name.upper()}",
                    expand=2,
                    hint_text="min,max",
                    data=f"{name}_Max",
                    border=ft.InputBorder.UNDERLINE,
                ),
                ft.TextField(
                    label="Count",
                    expand=1,
                    data=f"{name}_K",
                    border=ft.InputBorder.UNDERLINE,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            data=name,
        )

    def __build_card(self):
        self.newruls = ft.Column(
            spacing=5,
            controls=[
                self.__get_note(),
                self.__get_range_count("a"),
                self.__command_button(),
            ],
        )
        cols = ft.Column(
            tight=True,
            spacing=0,
            controls=[
                ft.Container(
                    alignment=ft.Alignment.CENTER_LEFT,
                    padding=ft.Padding(12, 5, 12, 5),
                    content=ft.Text("Add new game rules.", size=16),
                ),
                ft.Container(
                    border=ft.Border(
                        top=ft.BorderSide(
                            1, ft.Colors.with_opacity(0.3, DraculaColors.FOREGROUND)
                        ),  # 宽度为 3, 颜色为蓝色
                    ),
                    bgcolor=ft.Colors.with_opacity(0.6, DraculaColors.CRADBG),
                    border_radius=10,
                    padding=ft.Padding(12, 5, 12, 5),
                    content=self.newruls,
                ),
            ],
        )

        return cols

    def handle_add(self):
        self.row_name_char += 1
        new_row = self.__get_range_count(f"{chr(self.row_name_char)}")
        temp_len = len(self.newruls.controls)
        self.newruls.controls.insert(temp_len - 1, new_row)

    def handle_Cancel(self):
        self.visible = False
        self.update()

    async def handle_Apply(self):
        temp = self.templejson.copy()
        rows = self.newruls.controls
        for _item in rows:
            if isinstance(_item, ft.TextField):
                temp["randomData"]["note"] = (
                    _item.value or "Jackptot lotter new game rule."
                )
                continue
            if isinstance(_item, ft.Row):
                label = ""
                label_value = {}
                for _child_item in _item.controls:
                    if not isinstance(_child_item, ft.TextField):
                        continue
                    if _child_item.label.startswith("P"):
                        label = _child_item.label
                        label_value.update(self.Convert_to_list(_child_item.value))
                    if _child_item.label.startswith("C"):
                        count = (
                            int(_child_item.value) if _child_item.value.isdigit() else 0
                        )
                        label_value.update({"count": count})
                if label == "" or not label_value["enabled"]:
                    continue
                temp["randomData"][label] = label_value
        global jackpot_seting
        logr.info(f"bind temple dict {temp} {jackpot_seting}")
        with open(jackpot_seting, "w", encoding="utf-8") as f:
            json.dump(temp, f, indent=4, ensure_ascii=False)
        self.page.session.store.set("settings", temp)
        if self.render_filters:
            self.render_filters()
        self.handle_Cancel()

    def Convert_to_list(self, lable_value: str):
        """处理用户输入"""
        if lable_value in [None, ""]:
            return {"enabled": False}
        mathch = re.findall(r"(\d+)", lable_value)
        if mathch:
            value = [int(x) for x in mathch if x.isdigit()]
            range_start = min(value)
            range_end = max(value)
            if range_start == range_end:
                range_start = 0
            return {"range_start": range_start, "range_end": range_end, "enabled": True}
        return {"enabled": False}


# endregion


# region showRulev2
class showRulev2(ft.Container):
    def __init__(self):
        super().__init__()
        self.width = float("inf")
        self.border = ft.Border.all(
            1, ft.Colors.with_opacity(0.4, DraculaColors.ORANGE)
        )
        self.border_radius = 10
        self.runloadpage = False
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.content = self.__build_content()

    def did_mount(self):
        self.running = True
        self.page.run_task(self.loadpage)
        self.page.run_task(self.__update_card)

    def will_unmount(self):
        self.running = False

    async def loadpage(self):
        if self.runloadpage:
            await asyncio.sleep(0.2)
            return

        def offset():
            refcan = {"x": [1, 200], "y": [1, 10]}
            _offset = {name: random.randint(x, y) for name, (x, y) in refcan.items()}
            return _offset

        def black():
            color = RandColor()
            size = random.randint(5, 30)
            return ft.Container(
                width=size,
                height=size,
                bgcolor=ft.Colors.with_opacity(0.2, color),
                border_radius=size / 2,
                offset=ft.Offset(**offset()),
                # animate=ft.Animation(10000,ft.AnimationCurve.SLOW_MIDDLE),
            )

        for i in range(70):
            tempblack = black()
            self.Stack.controls.insert(0, tempblack)
            self.Stack.update()
            await asyncio.sleep(0.2)
        self.runloadpage = True

    def __build_content(self):
        """pass"""
        self.tips = ft.Text(
            "💡 Load page...",
            size=15,
            color=ft.Colors.with_opacity(0.6, DraculaColors.GREEN),
        )
        self.neirong = ft.Column(
            tight=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=[self.tips],
        )

        self.Stack = ft.Stack(
            width=float("inf"),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            controls=[
                ft.Container(
                    padding=12,
                    width=float("inf"),
                    content=self.neirong,
                ),
            ],
        )
        return self.Stack

    def update_tips(self, value: str, color: str):
        self.tips.value = f"💡 {value}"
        self.tips.color = ft.Colors.with_opacity(0.6, color)
        self.tips.update()

    def updateCard(self):
        self.page.run_task(self.__update_card)

    async def __load_json_setting(self):
        apply_rule = self.page.session.store.get("settings")
        if apply_rule:
            return apply_rule
        json_path = pathlib.Path(jackpot_seting)
        if not json_path.exists():
            return
        try:
            with json_path.open(mode="r", encoding="UTF-8") as r:
                temp = json.load(r)
                # logr.info(f'temp: {temp}')
                self.page.session.store.set("settings", temp)
                return temp
        except Exception as er:
            self.update_tips("Load json setting run error.", "#ee0f0f")
            logr.error(f"__load_json_setting run error.", {er})
            return

    async def __update_card(self):
        self.update_tips(
            "Run work update card.",
            "#0f9cee",
        )
        await asyncio.sleep(0.5)
        apply_rule = await self.__load_json_setting()
        if not apply_rule:
            self.update_tips(
                "Please add game rules. You can customize them using [new rule] or use the preset options.",
                "#eec90f",
            )
            return
        randomDatax = apply_rule.get("randomData", None)
        if not randomDatax:
            self.update_tips("No relevant data was found for randomData.", "#ee290f")
            return
        self.neirong.controls = [
            self.display_note(randomDatax["note"]),
            self.display_rules(randomDatax),
        ]
        self.neirong.update()

    def display_rules(self, pn: dict):
        rules = []
        for key, item in pn.items():
            if f"{key}".lower().startswith("p") and isinstance(item, dict):
                # PA Number Selection Rules: Choose 5 out of 36.
                if item["enabled"] == False:
                    continue
                ranges = item.get("range_end", 0)
                count = item.get("count", 0)
                rules.append(
                    ft.Text(
                        value=f"{key} Number Selection Rules: Choose {count} out of {ranges}.",
                        size=16,
                        color=ft.Colors.with_opacity(
                            0.6, color=DraculaColors.FOREGROUND
                        ),
                    )
                )
                # end
        example = randomData(seting=pn).get_exp()
        conter = ft.Container(
            padding=12,
            border_radius=10,
            width=float("inf"),
            bgcolor=ft.Colors.with_opacity(0.1, RandColor()),
            content=ft.Column(
                spacing=0,
                tight=True,
                controls=[
                    ft.Text(
                        "Basic number selection rules".upper(),
                        size=10,
                        color=ft.Colors.with_opacity(
                            0.3, color=DraculaColors.FOREGROUND
                        ),
                    ),
                    *rules,
                    ft.Text(
                        "Example Number".upper(),
                        size=10,
                        color=ft.Colors.with_opacity(
                            0.3, color=DraculaColors.FOREGROUND
                        ),
                    ),
                    self.displayNumbers(example, 25),
                    # ft.Text(f'{note}', color=DraculaColors.FOREGROUND, size=16),
                ],
            ),
        )
        return conter

    def display_note(self, note: str):
        conter = ft.Container(
            padding=12,
            border_radius=10,
            width=float("inf"),
            bgcolor=ft.Colors.with_opacity(0.3,RandColor()),
            # blend_mode=ft.BlendMode.SCREEN,
            content=ft.Column(
                spacing=0,
                tight=True,
                controls=[
                    ft.Text(
                        "Rules and Regulations".upper(),
                        size=10,
                        color=ft.Colors.with_opacity(
                            0.3, color=DraculaColors.FOREGROUND
                        ),
                    ),
                    ft.Text(f"{note}", color=DraculaColors.FOREGROUND, size=16),
                ],
            ),
        )
        return conter

    def displayNumbers(self, text: str, size: int = 35):
        """用环形标示 标识出数字"""
        result = re.findall(r"\d+|\+", text)
        row = ft.Row(
            wrap=True,
            # expand=True,
            spacing=5,
            run_spacing=5,
        )
        colors = [["#d9dbdf", "#747fdf"], ["#eab425", "#fbbf24"]]
        quan, shuzi = colors[0]
        for key in result:
            if key == "+":
                quan, shuzi = colors[1]
                continue
            item = ft.Container(
                content=ft.Text(
                    value=f"{key}",
                    size=size * 0.5,  # 字体大小约为容器的一半
                    weight=ft.FontWeight.BOLD,
                    color=shuzi,  # 文字建议也用金色系或对比色
                    text_align=ft.TextAlign.CENTER,
                ),
                bgcolor=ft.Colors.TRANSPARENT,  # 背景透明
                border=ft.Border.all(1, quan),
                width=size,
                height=size,
                border_radius=size / 2,
                # padding=ft.Padding.all(5),
                alignment=ft.Alignment.CENTER,
            )
            row.controls.append(item)
        return row

# endregion



# region DefaultSettings
class DefaultSettings(ft.Container):
    """默认设置指示器"""

    def __init__(self):
        super().__init__()
        self.width = float("inf")
        self.border = ft.Border.all(
            1, ft.Colors.with_opacity(0.6, DraculaColors.COMMENT)
        )
        self.bgcolor = ft.Colors.with_opacity(0.4, DraculaColors.COMMENT)
        self.border_radius = 10
        self.content = self.__build_card()
        # self.apply_rule = {}
        self.render_filters = None
        self.add_rule = None

    def setting_add_rule(self, add_rule=None):
        self.add_rule = add_rule

    def setting_render_filters(self, render_filters=None):
        self.render_filters = render_filters

    def did_mount(self):
        self.running = True
        self.page.run_task(self.__Lotter_Data)

    def will_unmount(self):
        self.running = False

    async def __Lotter_Data(self):
        """加载彩票预设数据并生成按钮"""
        # --- 构造按钮列表 ---
        if self.running:
            await asyncio.sleep(0.5)

            button_list = []

            # 注意：Lotter_Data 应该在函数外部定义或作为参数传入
            for k, item in Lotter_Data.items():
                description = item.get("description", "")
                button_list.append(
                    ft.TextButton(
                        content=f"{k}",
                        tooltip=ft.Tooltip(message=description),
                        # 【重要】使用默认参数 data=item 来破解 Lambda 闭包陷阱
                        on_click=lambda e, name=k, data=item, desc=description: (
                            self.save_preset_to_file(name, data, desc)
                        ),
                    )
                )
            self.defrow.controls = button_list
            self.update()

    def handle_add_rule(self, e):
        if self.add_rule:
            self.add_rule()

    def save_preset_to_file(self, name: str, preset_data: dict, desc: str):
        """将处理后的预设数据写入 json 文件"""
        # 1. 构造符合你要求的嵌套格式
        valid_json = {
            "randomData": {
                "note": f"{desc}",
            }
        }

        # 2. 解析 Lotter_Data 项并转换格式
        # 我们需要找到像 SA, SB, PA 这样的键，并匹配对应的 _K 键
        keys = preset_data.keys()
        for k in list(keys):
            # 过滤掉描述字段和数量字段(_K)，只处理 SA, SB, PA 等
            if k == "description" or k.endswith("_K"):
                continue

            count_key = f"{k}_K"
            if count_key in keys:
                # 转换键名：将 SA 转换为 PA, SB 转换为 PB (或者保持原样，取决于你的 UI 需求)
                # 这里假设你的 UI 统一使用 PA, PB, PC，我们做一个简单的映射
                target_key = k.replace("SA", "PA").replace("SB", "PB")

                valid_json["randomData"][target_key] = {
                    "enabled": True,
                    "range_start": preset_data[k][0],
                    "range_end": preset_data[k][1],
                    "count": preset_data[count_key],
                }

        with open(jackpot_seting, "w", encoding="utf-8") as f:
            json.dump(valid_json, f, indent=4, ensure_ascii=False)
            # self.page.show_dialog(
            #     get_snack_bar(f"Preset '{name}' has been applied and saved.")
            # )
        self.page.session.store.set("settings", valid_json)
        if self.render_filters:
            self.render_filters()

    async def Regenerate_handle_click(self, e):
        id = f"{randomData.generate_secure_string(8)}"
        self.stored_id = os.path.join(app_temp_path, f"gen_{id}.dict")
        filePath = pathlib.Path(self.stored_id)
        for item in filePath.parent.iterdir():
            if (
                item.is_file() or item.is_symlink() and item.name.startswith("gen_")
            ):  # 确保只删除文件
                logr.info(f"Regenerate_id Delete {item.name}.")
                item.unlink()
        filePath.parent.mkdir(parents=True, exist_ok=True)
        filePath.write_text("")
        self.page.show_dialog(ft.SnackBar(f"Regenerate id {id}"))

    def __build_card(self):
        self.defrow = ft.Row(
            controls=[],
            spacing=2,
            run_spacing=2,
            wrap=True,
            alignment=ft.MainAxisAlignment.START,
        )
        add_rule = ft.Button(
            bgcolor=DraculaColors.GREEN,
            color=DraculaColors.BACKGROUND,
            icon=ft.Icons.ADD_CIRCLE_OUTLINE,
            content="new rule",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            tooltip=ft.Tooltip(message="new game rule"),
            on_click=self.handle_add_rule,
        )
        Regenerate = ft.Button(
            bgcolor=ft.Colors.with_opacity(0.7, RandColor()),
            color=DraculaColors.BACKGROUND,
            icon=ft.Icons.REFRESH,
            content="Regenerate",
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
            tooltip=ft.Tooltip(message="ID Regeneration"),
            on_click=self.Regenerate_handle_click,
        )
        uibuttens = ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    padding=12,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.5, DraculaColors.CRADBG),
                    border=ft.Border(
                        bottom=ft.BorderSide(
                            1, ft.Colors.with_opacity(0.4, DraculaColors.COMMENT)
                        ),  # 宽度为 3, 颜色为蓝色
                    ),
                    width=float("inf"),
                    content=self.defrow,
                ),
                ft.Container(
                    padding=ft.Padding(12, 5, 12, 5),
                    bgcolor=ft.Colors.TRANSPARENT,
                    content=ft.Row(
                        controls=[Regenerate, add_rule],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ),
            ],
        )
        return uibuttens


# endregion


# region SetingsPage
class SetingsPage:
    """设置页面类"""

    def __init__(self):
        self.rule_mode_show = showRulev2()
        self.uese_input_mode = input_user_rule()
        self.default_setings = DefaultSettings()
        # self.User_Directory = UserDirectory()
        self.apply_rule = {}

        self.uese_input_mode.setting_render_filters(self.render_filters)
        self.default_setings.setting_add_rule(self.open_dialog)
        self.default_setings.setting_render_filters(self.render_filters)
        self.view = self.get_seting_view()

    def get_Selection_line(self, Selection_name: str):
        name = f"P{Selection_name}"
        return ft.Row(
            controls=[
                ft.TextField(
                    label=name,
                    expand=2,
                    hint_text="min,max",
                    data=f"{name}_Max",
                    border=ft.InputBorder.UNDERLINE,
                ),
                ft.TextField(
                    label="Count",
                    expand=1,
                    data=f"{name}_K",
                    border=ft.InputBorder.UNDERLINE,
                ),
            ],
            # 给这一行打个标签，方便以后提取数据
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            data=name,
        )

    def render_filters(self):
        """渲染过滤器列表"""
        self.rule_mode_show.updateCard()

    def open_dialog(self):
        self.uese_input_mode.openCard()

    def get_seting_view(self):
        return ft.Column(
            controls=[
                # ft.Image(
                #     src="setting.png",
                #     fit=ft.BoxFit.FIT_HEIGHT,
                #     width=475 * 0.45,
                #     height=135 * 0.45,
                # ),
                ft.Text(
                    "Setting",
                    size=25,
                    weight="bold",
                    color=DraculaColors.COMMENT,
                    font_family="RacingSansOne-Regular",
                ),
                # 这里可以添加更多的设置控件
                ft.Divider(),
                # ft.Row(controls=self.buttons, scroll=ft.ScrollMode.HIDDEN, expand=True),
                # ft.Divider(),
                self.rule_mode_show,
                self.default_setings,
                self.uese_input_mode,
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )


# endregion
