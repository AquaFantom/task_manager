import flet as ft
from flet import (
    Column,
    Row,
    Text,
    Container,
    padding,
    TextButton,
    icons,
    ButtonStyle,
    colors,
    RoundedRectangleBorder,
    TextField,
    TextThemeStyle,
    PopupMenuButton,
    PopupMenuItem,
    TextAlign,
    border_radius,
    border,
    MainAxisAlignment,
)

from models import storage


class BoardItem(Container):
    def __init__(self, name, page):
        super().__init__()
        self.page = page
        self._board_name = name
        self._name_ref = ft.Ref[Text]()
        self.content = Container(
            content=Row(
                controls=[
                    Container(
                        content=Text(ref=self._name_ref, color=colors.BLACK),
                        data='',
                        expand=True,
                        on_click=self.go_to_board
                    ),
                    Container(
                        content=PopupMenuButton(  # контейнер с кнопкой всплывающего меню
                            items=[
                                PopupMenuItem(
                                    content=Text(
                                        value="Удалить", style=TextThemeStyle.LABEL_MEDIUM,
                                        text_align=TextAlign.CENTER
                                    ),
                                    on_click=self.delete,
                                ),
                                PopupMenuItem(
                                    content=Text(
                                        value="Переименовать", style=TextThemeStyle.LABEL_MEDIUM,
                                        text_align=TextAlign.CENTER,
                                    ),
                                    on_click=self.set_name
                                ),
                            ]
                        ),
                        padding=padding.only(right=-10),
                        border_radius=border_radius.all(3)
                    )],
                alignment=MainAxisAlignment.SPACE_BETWEEN,
            ),
            border=border.all(1, colors.BLACK38),
            border_radius=border_radius.all(5),
            bgcolor=colors.WHITE60 if self.page.theme_mode == ft.ThemeMode.LIGHT else colors.LIGHT_BLUE_50,
            padding=padding.all(10),
            width=250,
            data='',
            on_click=self.go_to_board
        )
        self._name_ref.current.value = name
        self.on_click = self.go_to_board

    def go_to_board(self, e):
        self.page.route = f'/boards/{self._board_name}'
        self.page.update()

    @property
    def name(self) -> str:
        return self._board_name

    @name.setter
    def name(self, value):
        storage.rename_board(self._board_name, value)
        self._board_name = value
        self._name_ref.current.value = value

    def set_name(self, e):
        def close_dlg(e):
            if (hasattr(e.control, "text") and not e.control.text == "Отмена") or (
                    type(e.control) is ft.TextField and e.control.value != ""
            ):
                self.name = dialog_text.value
            dialog.open = False
            self.page.update()

        def textfield_change(e):
            if dialog_text.value == "":
                rename_button.disabled = True
            else:
                rename_button.disabled = False
            self.page.update()

        dialog_text = TextField(
            label="Введите новое название", on_submit=close_dlg, on_change=textfield_change
        )
        rename_button = ft.ElevatedButton(
            text="Изменить", bgcolor=colors.BLUE_200, on_click=close_dlg, disabled=True
        )
        dialog = ft.AlertDialog(
            title=Text("Введите название"),
            content=Column(
                [
                    dialog_text,
                    Row(
                        [
                            ft.ElevatedButton(text="Отмена", on_click=close_dlg),
                            rename_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True,
            )
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        dialog_text.focus()

    def delete(self, e):
        storage.delete_board(self._board_name)
        parent: Row = self.parent
        parent.controls.remove(self)
        self.page.update()


class ListBoards(Column):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.boards = []
        self.controls = [
            Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Container(
                        Text(value="Ваши доски", style=TextThemeStyle.HEADLINE_MEDIUM),
                        padding=padding.only(top=15)),
                    Container(
                        TextButton(
                            "Добавить новую доску",
                            icon=icons.ADD,
                            on_click=self.add_board,
                            style=ButtonStyle(
                                color=colors.WHITE,
                                bgcolor={
                                    "": colors.LIGHT_BLUE_500,
                                    "hovered": colors.LIGHT_BLUE_600
                                },
                                shape={
                                    "": RoundedRectangleBorder(radius=3)
                                }
                            )
                        ),
                        padding=padding.only(right=50, top=15),
                    )
                ]),
            Row([
                TextField(
                    hint_text="Поиск доски", autofocus=False, content_padding=padding.only(left=10),
                    width=200, height=40, text_size=12,
                    border_color=colors.BLACK26, focused_border_color=colors.BLUE_ACCENT,
                    suffix_icon=icons.SEARCH,
                    on_change=self.search
                )
            ]),
            Row(controls=self.boards, wrap=True)
        ]
        self.load_data()

    def search(self, e):
        self.load_data(e.data)

    def load_data(self, filter_name: str = None):
        self.boards.clear()
        data = storage.load_file()
        for board_name in data:
            if filter_name is None:
                self.create_new_board(board_name)
                continue
            if board_name.lower().startswith(filter_name.lower()):
                self.create_new_board(board_name)
        self.page.update()

    def add_board(self, e):
        def close_dlg(e):
            if (hasattr(e.control, "text") and not e.control.text == "Отмена") or (
                    type(e.control) is ft.TextField and e.control.value != ""
            ):
                self.create_new_board(dialog_text.value)
                storage.add_board(dialog_text.value)
            dialog.open = False
            self.page.update()

        def textfield_change(e):
            if dialog_text.value == "":
                create_button.disabled = True
            else:
                create_button.disabled = False
            self.page.update()

        dialog_text = TextField(
            label="Введите название", on_submit=close_dlg, on_change=textfield_change
        )
        create_button = ft.ElevatedButton(
            text="Создать", bgcolor=colors.BLUE_200, on_click=close_dlg, disabled=True
        )
        dialog = ft.AlertDialog(
            title=Text("Введите название"),
            content=Column(
                [
                    dialog_text,
                    Row(
                        [
                            ft.ElevatedButton(text="Отмена", on_click=close_dlg),
                            create_button,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                tight=True
            )
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        dialog_text.focus()

    def create_new_board(self, board_name):
        new_board = BoardItem(name=board_name, page=self.page)
        self.boards.append(new_board)
