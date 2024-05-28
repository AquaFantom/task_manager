import flet as ft
from flet import (
    Text,
    colors,
    icons,
    AppBar,
    IconButton,
    NavigationDrawer
)
from flet_core.control_event import ControlEvent


class CustomAppBar(AppBar):
    def __init__(self, drawer: NavigationDrawer):
        self.drawer = drawer
        super().__init__()

        self.leading = IconButton(
            icons.DARK_MODE,
            icon_color=colors.WHITE,
            icon_size=30,
            on_click=self.move_theme
        )
        self.leading_width = 75
        self.title = Text("TaskManager", size=32, text_align="start", color=colors.WHITE, font_family="Comfortaa_Bold")
        self.center_title = False
        self.toolbar_height = 75
        self.bgcolor = colors.LIGHT_BLUE_500

    def move_theme(self, e):
        if self.page.theme_mode == ft.ThemeMode.DARK:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.leading.icon = ft.icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.leading.icon = ft.icons.DARK_MODE
        self.page.update()
