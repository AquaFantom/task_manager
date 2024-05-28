import flet as ft
from flet import (
    Page,
    Text
)

from views.board import Board
from views.list_boards import ListBoards
from views.menu import CustomAppBar


def main(page: Page):
    def change_route(e: ft.RouteChangeEvent):
        troute = ft.TemplateRoute(e.route)

        controller = None
        if troute.match("/not_found"):
            controller = ft.Container(Text('Страница не найдена', size=30), alignment=ft.alignment.center, expand=True)
        elif troute.match("/boards"):
            controller = ListBoards(page)
        elif troute.match("/boards/:name"):
            controller = Board(troute.name)

        if controller is None:
            page.route = "/not_found"
        else:
            page.controls = [controller]
        page.update()
    page.appbar = CustomAppBar(page.drawer)

    page.title = "TaskManager"
    page.padding = 30
    page.fonts = {"Comfortaa": "assets/fonts/Comfortaa-Medium.ttf",
                  "Comfortaa_Bold": "assets/fonts/Comfortaa-Bold.ttf"}
    page.theme = ft.Theme(
        font_family="Comfortaa",
        color_scheme=ft.ColorScheme(
            primary=ft.colors.BLUE_GREY_700
        )
    )
    page.on_route_change = change_route
    page.route = '/boards'
    page.update()


if __name__ == "__main__":
    ft.app(target=main)
