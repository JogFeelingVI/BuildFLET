# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2025-12-28 00:32:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-02 02:49:25

from . import snack_bar
import flet as ft
import json
import os

app_data_path = os.getenv("FLET_APP_STORAGE_DATA")
app_temp_path = os.getenv("FLET_APP_STORAGE_TEMP")
jackpot_seting = os.path.join(app_data_path, "jackpot_settings.json")

Lotter_Data = {
    "SSQ": {
        "description": "中国福利彩票双色球",
        "SA": [1, 33],
        "SB": [1, 16],
        "SA_K": 6,
        "SB_K": 1,
    },
    "KL8": {
        "description": "中国福利彩票快乐8",
        "PA": [1, 80],
        "PA_K": 10,
    },
    "Lotter52": {
        "description": "中国体育彩票大乐透",
        "PA": [1, 35],
        "PB": [1, 12],
        "PA_K": 5,
        "PB_K": 2,
    },
}


class Selectable(ft.Column):
    """setings page setings printx"""

    def __init__(
        self,
        text: str = "test",
        range_min: int = 1,
        range_max: int = 100,
        onff: bool = True,
    ):
        # 1. 初始化控件（去掉末尾逗号！）
        self.base_text = text
        self.counter_value = 5
        self.start = range_min
        self.end = range_max
        self.text_label = ft.Text(f"{self.base_text} {range_min}-{range_max}")
        self.range_slider = ft.RangeSlider(
            min=range_min,
            max=range_max,
            start_value=range_min,
            end_value=range_max,
            label="{value}",
            disabled=not onff,
            expand=True,  # 在 Row 中让 Slider 自动拉伸填满剩余空间
            on_change=self.handle_range_change,
        )
        self.switch_control = ft.Switch(
            label="ON" if onff else "OFF",
            value=onff,
            on_change=self.handle_switch_change,
        )

        # 第三行：计数器控件
        self.num_display = ft.Text(str(self.counter_value), size=20, weight="bold")

        self.counter_row = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.REMOVE,
                    on_click=self.handle_decrement,
                    disabled=not onff,  # 初始状态跟随开关
                ),
                self.num_display,
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    on_click=self.handle_increment,
                    disabled=not onff,  # 初始状态跟随开关
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
        )

        # 2. 调用父类初始化，直接传入控件列表
        super().__init__(
            controls=[
                # 第一行：标题和开关 左右分布
                ft.Row(
                    controls=[self.text_label, self.switch_control],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # 左右撑开,
                    expand=True,
                ),
                # 第二行：滑动条
                ft.Row(
                    controls=[self.range_slider],
                    alignment=ft.MainAxisAlignment.CENTER,
                    expand=True,
                ),
                ft.Row(controls=[self.counter_row], alignment=ft.MainAxisAlignment.END),
            ],
            spacing=10,  # 行与行之间的间距
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,  # 内部控件水平拉伸
        )

    # --- 事件处理 ---
    def handle_increment(self, e):
        self.counter_value += 1
        self.num_display.value = str(self.counter_value)
        self.update()

    def handle_decrement(self, e):
        if self.counter_value > 0:
            self.counter_value -= 1
            self.num_display.value = str(self.counter_value)
            self.update()

    def handle_range_change(self, e):
        """当滑动条范围改变时触发"""
        self.start = int(self.range_slider.start_value)
        self.end = int(self.range_slider.end_value)
        # 更新文本显示
        self.text_label.value = f"{self.base_text} {self.start}-{self.end}"
        # 注意：在自定义控件内部修改属性后，需要调用 self.update() 才能看到变化
        self.update()

    def handle_switch_change(self, e):
        """当开关状态改变时触发"""
        e_vale = self.switch_control.value
        self.switch_control.label = "ON" if e_vale else "OFF"
        # 如果开关关闭 (False)，则禁用滑动条 (disabled=True)
        self.range_slider.disabled = not e_vale
        self.counter_row.disabled = not e_vale
        self.update()

    def get_json(self):
        return {
            f"{self.base_text}": {
                "enabled": self.switch_control.value,
                "range_start": int(self.range_slider.start_value),
                "range_end": int(self.range_slider.end_value),
                "count": self.counter_value,
            }
        }

    def set_json(self, key: str, json_data_item: dict):
        self.base_text = key

        self.switch_control.value = json_data_item["enabled"]
        self.range_slider.disabled = not json_data_item["enabled"]
        self.counter_row.disabled = not json_data_item["enabled"]

        s = json_data_item.get("range_start", self.range_slider.min)
        e = json_data_item.get("range_end", self.range_slider.max)
        self.range_slider.start_value = s
        self.range_slider.end_value = e

        self.counter_value = json_data_item["count"]
        self.num_display.value = str(self.counter_value)  # 必须更新已有控件的 value

        # 2. 更新标题文字 (修改已有控件的属性，而不是创建新控件)
        self.text_label.value = f"{self.base_text} {int(s)}-{int(e)}"

        return self


#! 上面的代码已近废弃


def load_Lotter_Data(page: ft.Page):
    """加载彩票预设数据并生成按钮"""

    def save_preset_to_file(name: str, preset_data: dict):
        """将处理后的预设数据写入 json 文件"""
        # 1. 构造符合你要求的嵌套格式
        valid_json = {
            "randomData": {
                "note": "save setings from preset buttons",
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
            page.show_dialog(
                snack_bar.get_snack_bar(f"Preset '{name}' has been applied and saved.")
            )

    # --- 构造按钮列表 ---
    button_list = []
    # 注意：Lotter_Data 应该在函数外部定义或作为参数传入
    for k, item in Lotter_Data.items():
        button_list.append(
            ft.Button(
                f"{k}",
                # 【重要】使用默认参数 data=item 来破解 Lambda 闭包陷阱
                on_click=lambda e, name=k, data=item: save_preset_to_file(name, data),
            )
        )
    return button_list


def get_seting_view(page: ft.Page):
    """返回设置页面视图"""

    filter_items_column = ft.Column(spacing=10)
    buttons = load_Lotter_Data(page)

    def open_dialog(index=-1):
        page.update()
        # 占位函数，实际逻辑在 main.py 中实现

    setting_view = ft.Column(
        controls=[
            ft.Text("Settings", size=25, weight="bold"),
            ft.Button(
                "Add game rules", icon=ft.Icons.ADD, on_click=lambda _: open_dialog(-1)
            ),
            # 这里可以添加更多的设置控件
            ft.Divider(),
            ft.Row(controls=buttons, scroll=ft.ScrollMode.HIDDEN, expand=True),
            ft.Divider(),
            ft.Column(
                [filter_items_column], scroll=ft.ScrollMode.ADAPTIVE, expand=True
            ),
        ],
        expand=True,
        scroll=ft.ScrollMode.HIDDEN,
    )
    return setting_view
