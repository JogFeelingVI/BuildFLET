# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-07 11:39:47
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-07 14:38:38


from .DraculaTheme import DraculaColors, RandColor
import flet as ft


class adbx(ft.AlertDialog):
    def __init__(self, uc: str, content: ft.Control):
        self.userColor = uc if uc else RandColor(mode="Galss")
        self.shape = ft.RoundedRectangleBorder(
            radius=10,
            side=ft.BorderSide(2, self.userColor),
        )
        self._ucontent = content
        self.running = False
        self.did_mount_callback = None

        super().__init__(
            content=self.__build_conter(),
            content_padding=0,
            title_padding=0,
            actions_padding=0,
            modal=True,
            bgcolor=ft.Colors.TRANSPARENT,
        )

    def setting_did_mount_callback(self, didcallback=None):
        self.did_mount_callback = didcallback

    def did_mount(self):
        self.running = True
        if self.did_mount_callback:
            self.page.run_task(self.did_mount_callback)

    def will_unmount(self):
        self.running = False

    def __build_conter(self):
        conter = ft.Container(
            padding=12,
            width=400,
            border_radius=10,
            border=ft.Border.all(1, self.userColor),
            bgcolor=ft.Colors.with_opacity(0.9, "#252525"),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=self.userColor,
                offset=ft.Offset(0, 0),
            ),
        )
        conter.content = self._ucontent if self._ucontent else None
        return conter
