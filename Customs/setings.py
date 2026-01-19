# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-19 02:15:27

from .lotteryballs import LotteryBalls
from .SnackBar import get_snack_bar
from .DraculaTheme import DraculaColors
from .jackpot_core import randomData
import flet as ft
import json
import os
import re
import asyncio

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")

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


class showRule(ft.Card):
    def __init__(self):
        super().__init__()
        self.content = self.__build_card()

    def did_mount(self):
        self.running = True
        self.updateCard()

    def will_unmount(self):
        self.running = False

    def updateCard(self):
        self.page.run_task(self.__update_card)

    async def __update_card(self):
        if not self.running:
            return
        apply_rule = self.page.session.store.get("settings")
        if not apply_rule:
            return
        randomDatax = apply_rule.get("randomData", None)
        if not randomDatax:
            return
        example = randomData(seting=randomDatax).get_exp()
        textlist = [LotteryBalls(example,32,"LE"), ft.Divider()]
        for key, item in randomDatax.items():
            if key == "note":
                textlist.append(
                    ft.Text(
                        f"🚩Note: {item}",
                        size=15,
                        weight="bold",
                        color=DraculaColors.ORANGE,
                        max_lines=2,
                    )
                )
                continue
            # print(f'{key} {item} ==-==')
            count_range = f"{item['range_start']} - {item['range_end']}"
            count = item["count"]

            textlist.append(
                ft.Text(
                    f"Section [ {key} ].  Choose {count} number from {count_range}.",
                    max_lines=2,
                    color=DraculaColors.PURPLE,
                    size=15,
                )
            )
        self.content.content.controls = textlist
        self.update()

    def __build_card(self):
        print("bulid card is running.")
        return ft.Container(
            padding=12,
            # expand=True,
            # opacity=0.65,
            width=float("inf"),
            border=ft.Border.all(2, DraculaColors.COMMENT),
            border_radius=10,
            content=ft.Column(
                tight=True,
                controls=[
                    # LotteryBalls(exp, align="LE"),
                    # ft.Divider(),
                    # *textlist,
                    ft.Text(
                        "💡Please add game rules. You can customize them using [new rule] or use the preset options."
                    ),
                ],
            ),
        )


class DefaultSettings(ft.Card):
    """默认设置指示器"""

    def __init__(self, add_rule=None, callback=None):
        super().__init__()
        self.content = self._build_default_bu()
        self.apply_rule = {}
        self.callback = callback
        self.add_rule = add_rule

    def did_mount(self):
        self.running = True
        self.page.run_task(self._Lotter_Data)

    def will_unmount(self):
        self.running = False

    async def _Lotter_Data(self):
        """加载彩票预设数据并生成按钮"""
        # --- 构造按钮列表 ---
        if self.running:
            await asyncio.sleep(1)

            add_rule = ft.Button(
                icon=ft.Icons.RULE,
                content="new rule",
                tooltip=ft.Tooltip(message="new game rule"),
                on_click=self.handle_add_rule,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=2),
                    color=DraculaColors.FOREGROUND,
                    bgcolor=DraculaColors.COMMENT,
                    overlay_color=DraculaColors.PINK,
                    side=ft.BorderSide(
                        1,
                        DraculaColors.FOREGROUND,
                        ft.BorderSideStrokeAlign.INSIDE,
                        ft.BorderStyle.SOLID,
                    ),
                ),
            )
            button_list = [add_rule]

            # 注意：Lotter_Data 应该在函数外部定义或作为参数传入
            for k, item in Lotter_Data.items():
                description = item.get("description", "")
                button_list.append(
                    ft.TextButton(
                        content=f"{k}",
                        tooltip=ft.Tooltip(message=description),
                        # 【重要】使用默认参数 data=item 来破解 Lambda 闭包陷阱
                        on_click=lambda e,
                        name=k,
                        data=item,
                        desc=description: self.save_preset_to_file(name, data, desc),
                    )
                )
            self.content.content.controls = button_list
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
            self.page.show_dialog(
                get_snack_bar(f"Preset '{name}' has been applied and saved.")
            )
        self.apply_rule = valid_json
        if self.callback:
            self.callback()

    def _build_default_bu(self):
        return ft.Container(
            padding=10,
            width=float("inf"),
            border=ft.Border.all(2, DraculaColors.COMMENT),
            border_radius=10,
            content=ft.Row(
                controls=[],
                spacing=2,
                run_spacing=2,
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
            ),
        )


class UserDirectory(ft.Card):
    """用户目录指示器"""

    def __init__(self):
        super().__init__()
        self.stored_dir = None
        self.tips = ft.Text(
            "💡 Tip: Set the user directory to store filter files and saved images.",
            color=DraculaColors.FOREGROUND,
            size=12,
            max_lines=2,
            # overflow=ft.TextOverflow.ELLIPSIS,
            no_wrap=False,
        )
        self.button = ft.Button(
            "User Directory",
            icon=ft.Icons.FOLDER_OFF,
            on_click=lambda _: self.page.run_task(self.select_user_dif),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=2),
                color=DraculaColors.FOREGROUND,
                bgcolor=DraculaColors.COMMENT,
                overlay_color=DraculaColors.PINK,
                side=ft.BorderSide(
                    1,
                    DraculaColors.FOREGROUND,
                    ft.BorderSideStrokeAlign.INSIDE,
                    ft.BorderStyle.SOLID,
                ),
            ),
        )
        self.content = self._build_UI()
        self.count = 10

    def did_mount(self):
        self.running = True
        self.page.run_task(self.update_ui)

    def will_unmount(self):
        self.running = False

    def _build_UI(self):
        return ft.Container(
            padding=10,
            # width=200,
            width=float("inf"),
            border=ft.Border.all(2, DraculaColors.COMMENT),
            border_radius=10,
            content=ft.Row(
                controls=[
                    self.tips,
                    self.button,
                ],
                spacing=5,
                wrap=True,
                # tight=True,
                alignment=ft.MainAxisAlignment.START,
            ),
        )

    async def update_ui(self):
        if self.running:
            await asyncio.sleep(1)  # 初始延迟，确保页面加载完成

            temp = await self.getuser_dir()
            print(f"Checking user directory...{temp=}")
            if temp:
                self.tips.value = f"📂 User Directory: {temp}"
                self.button.visible = False
                self.page.update()

    async def getuser_dir(self):
        """获取用户目录"""
        temp = await self.page.shared_preferences.get("user_dir")
        if self.page.web:
            temp = app_data_path
        print(f"Fetched user directory: {temp=}")
        return temp

    async def select_user_dif(self):
        if not self.page.web:
            picked_dir = await ft.FilePicker().get_directory_path(
                dialog_title="Please select a directory?"
            )
            if picked_dir:
                await self.page.shared_preferences.set("user_dir", picked_dir)
                await self.update_ui()


class SetingsPage:
    """设置页面类"""

    def __init__(self, page: ft.Page):
        self.page = page
        # self.buttons = self.load_Lotter_Data()
        self.add_button_row = ft.Row(
            controls=[
                ft.Button("Add Row", icon=ft.Icons.ADD, on_click=self.handle_add_click)
            ],
            alignment=ft.MainAxisAlignment.END,
        )
        # self.Fab = ft.FloatingActionButton(
        #     icon=ft.Icons.RULE,
        #     bgcolor=DraculaColors.PURPLE,
        #     on_click=lambda _: self.open_dialog(),
        #     # opacity=0.65,
        # )
        self.note_text = ft.TextField(
            label="Note",
            hint_text="Rule Settings Instructions",
            expand=1,
            border=ft.InputBorder.UNDERLINE,
        )
        self.selection_container = ft.Column(
            controls=[
                ft.Row(
                    controls=[self.note_text],
                    tight=True,
                ),
                self.get_Selection_line("A"),
                self.add_button_row,
            ],
            tight=True,
            spacing=10,
        )
        self.rule_mode_show = showRule()
        self.default_setings = DefaultSettings(self.open_dialog, self.render_filters)
        self.apply_rule = {}

        # self.filter_items_column = ft.Column(spacing=10)
        self.dlg = self.get_dlg()
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

    def Processing_user_input(self, cdvalue: str):
        """处理用户输入"""
        if cdvalue in [None, ""]:
            return None
        mathch = re.findall(r"(\d+)", cdvalue)
        if mathch:
            val = [int(x) for x in mathch if x.isdigit()]
            return val if len(val) == 2 else val[0]
        return None

    def handle_apply(self):
        # 获取所有输入行的数据逻辑
        Rows_data = {"note": self.note_text.value or "setting game rule"}
        for control in self.selection_container.controls:
            if not hasattr(control, "data"):
                continue  # 只有输入行有 data 属性
            tag = control.data  # 提取标签名 P...
            Rows_data[tag] = {}
            try:
                for _child in control.controls:
                    if not isinstance(_child, ft.TextField):
                        continue
                    _cd = _child.data
                    _cd_val = _child.value
                    _cd_val = self.Processing_user_input(_cd_val)
                    if _cd_val is None:
                        continue
                    if _cd.endswith("_Max"):
                        if isinstance(_cd_val, list) and len(_cd_val) == 2:
                            Rows_data[tag]["range_start"] = _cd_val[0]
                            Rows_data[tag]["range_end"] = _cd_val[1]
                        elif isinstance(_cd_val, int):
                            Rows_data[tag]["range_start"] = 1
                            Rows_data[tag]["range_end"] = _cd_val
                    if _cd.endswith("_K"):
                        Rows_data[tag]["count"] = _cd_val
                    Rows_data[tag]["enabled"] = True
            except Exception:
                self.page.show_dialog(get_snack_bar("Rule settings error.", "error"))
        Rows_data = {k: v for k, v in Rows_data.items() if v not in [None, {}]}
        json_data = {"randomData": Rows_data.copy()}
        with open(jackpot_seting, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4, ensure_ascii=False)
        self.page.show_dialog(get_snack_bar(f"Game rules have been set."))
        self.apply_rule = json_data
        self.dlg.open = False
        self.render_filters()
        self.page.update()

    def handle_add_click(self, e):
        # 计算当前已有多少个输入行 (排除掉底部的 Add 按钮行)
        # 减 1 是因为最后一行是按钮行
        current_count = len(self.selection_container.controls) - 2
        # 字母排序 A, B, C...
        new_name = chr(65 + current_count)  # 65 是 'A'
        # 创建新行
        new_line = self.get_Selection_line(new_name)

        # 【关键】将新行插入到倒数第一位（即 Add 按钮的上方）
        self.selection_container.controls.insert(
            len(self.selection_container.controls) - 1, new_line
        )
        # 【关键】刷新容器，让新行显示出来
        self.selection_container.update()

    def render_filters(self):
        """渲染过滤器列表"""
        # self.filter_items_column.controls.clear()
        self.apply_rule = self.default_setings.apply_rule
        self.page.session.store.set("settings", self.apply_rule)
        self.rule_mode_show.updateCard()
        # randomDatax = self.apply_rule.get("randomData", {})
        # rd = randomData(seting=randomDatax)
        # exp = rd.get_exp()
        # textlist = []
        # for key, item in randomDatax.items():
        #     if key == "note":
        #         continue
        #     # print(f'{key} {item} ==-==')
        #     count_range = f"{item['range_start']} - {item['range_end']}"
        #     count = item["count"]

        #     textlist.append(
        #         ft.Text(
        #             f"Section [ {key} ].  Choose {count} number from {count_range}.",
        #             max_lines=2,
        #             color=DraculaColors.PURPLE,
        #             size=15,
        #         )
        #     )
        # rule_mode_show = ft.Card(
        #     # bgcolor=DraculaColors.CURRENT_LINE,
        #     show_border_on_foreground=True,
        #     content=ft.Container(
        #         padding=12,
        #         # expand=True,
        #         # opacity=0.65,
        #         content=ft.Column(
        #             tight=True,
        #             controls=[
        #                 LotteryBalls(exp, align="LE"),
        #                 ft.Text(
        #                     f"🚩Note: {randomDatax['note']}",
        #                     size=15,
        #                     weight="bold",
        #                     color=DraculaColors.ORANGE,
        #                     max_lines=2,
        #                 ),
        #                 ft.Divider(),
        #                 *textlist,
        #             ],
        #         ),
        #     ),
        # )
        # rule_mode_show = showRule()
        # self.filter_items_column.controls.append(rule_mode_show)
        self.page.update()

    def close_dlg(self):
        self.dlg.open = False
        self.page.update()

    def get_dlg(self):
        dlg = ft.AlertDialog(
            title=ft.Text("add new game rules", color=DraculaColors.COMMENT),
            content=ft.Container(
                content=self.selection_container,
                width=350,  # 锁定宽度防止抖动
            ),
            actions=[
                ft.TextButton("Cancel", on_click=lambda _: self.close_dlg()),
                ft.Button(
                    "Apply",
                    bgcolor=DraculaColors.RED,
                    color=DraculaColors.FOREGROUND,
                    on_click=lambda _: self.handle_apply(),
                ),
            ],
        )
        return dlg

    def open_dialog(self):
        self.dlg.open = True
        self.page.update()

    def get_seting_view(self):
        self.page.overlay.append(self.dlg)

        return ft.Column(
            controls=[
                ft.Image(
                    src="setting.png",
                    fit=ft.BoxFit.FIT_HEIGHT,
                    width=475 * 0.45,
                    height=135 * 0.45,
                ),
                # ft.Text("Setting", size=25, weight="bold", color=DraculaColors.COMMENT),
                # 这里可以添加更多的设置控件
                ft.Divider(),
                # ft.Row(controls=self.buttons, scroll=ft.ScrollMode.HIDDEN, expand=True),
                # ft.Divider(),
                self.rule_mode_show,
                UserDirectory(),
                self.default_setings,
            ],
            expand=True,
            scroll=ft.ScrollMode.HIDDEN,
        )
