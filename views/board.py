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
    Draggable,
    DragTarget,
)
from flet_core.drag_target import DragTargetEvent

from models import storage


class TaskItem(Draggable):
    def __init__(self, board: str, status: str, name: str):
        super().__init__()
        self.board_name = board
        self.status_name = status
        self._task_name = name
        self._task_name_ref = ft.Ref[Text]()
        self.content = Container(
            bgcolor=colors.LIGHT_BLUE_50,
            content=Row([
                Container(
                    content=Text(value=self._task_name, ref=self._task_name_ref, color=colors.BLACK), data='', expand=True, on_click=''),
                Container(
                    content=PopupMenuButton(  # контейнер с кнопкой всплывающего меню
                        items=[
                            PopupMenuItem(
                                content=Text(
                                    value="Удалить", style=TextThemeStyle.LABEL_MEDIUM,
                                    text_align=TextAlign.CENTER
                                ),
                                on_click=self.delete_button,
                            ),
                            PopupMenuItem(
                                content=Text(
                                    value="Переименовать", style=TextThemeStyle.LABEL_MEDIUM,
                                    text_align=TextAlign.CENTER,
                                ),
                                on_click=self.set_name
                            )
                        ]
                    ),
                    padding=padding.only(right=-10),
                    border_radius=border_radius.all(3)
                )], alignment=MainAxisAlignment.SPACE_BETWEEN),
            border_radius=border_radius.all(5),
            padding=padding.all(10),
            width=250,
            data=''
        )

    @property
    def name(self) -> str:
        return self._task_name

    @name.setter
    def name(self, value):
        storage.rename_task(self.board_name, self.status_name, self._task_name, value)
        self._task_name = value
        self._task_name_ref.current.value = value

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

    def delete_button(self, e):
        self.delete()

    def delete(self):
        storage.delete_task(self.board_name, self.status_name, self.name)
        parent = self.parent
        parent.controls.remove(self)
        self.page.update()


class StatusColumn(DragTarget):
    def __init__(self, board, name):
        super().__init__()
        self.board_name = board
        self.on_accept = self.move_task
        self.alignment = ft.alignment.top_left
        self._status_name = name
        self._status_name_ref = ft.Ref[Text]()
        self.task_ref = ft.Ref[Column]()
        self.content = Container(
            bgcolor=colors.BLUE_200,
            border_radius=border_radius.all(5),
            content=Column(
                controls=[
                    Container(
                        content=Row(
                            controls=[
                                Container(
                                    content=Text(ref=self._status_name_ref, color=colors.BLACK), data='', expand=True, on_click=''
                                ),
                                ft.IconButton(
                                    icon=ft.icons.ADD, on_click=self.add_task
                                ),
                                Container(
                                    content=PopupMenuButton(  # контейнер с кнопкой всплывающего меню
                                        items=[
                                            PopupMenuItem(
                                                content=Text(
                                                    value="Переименовать", style=TextThemeStyle.LABEL_MEDIUM,
                                                    text_align=TextAlign.CENTER,
                                                ),
                                                on_click=self.set_name
                                            ),
                                            PopupMenuItem(
                                                content=Text(
                                                    value="Удалить", style=TextThemeStyle.LABEL_MEDIUM,
                                                    text_align=TextAlign.CENTER
                                                ),
                                                on_click=self.delete,
                                            ),
                                            PopupMenuItem(
                                                content=Text(
                                                    value="Удалить все задачи", style=TextThemeStyle.LABEL_MEDIUM,
                                                    text_align=TextAlign.CENTER
                                                ),
                                                on_click=self.clear
                                            )
                                        ]
                                    ),
                                    padding=padding.only(right=-10),
                                )
                            ],
                        ),
                        border_radius=border_radius.all(5),
                        bgcolor=colors.LIGHT_BLUE_500,
                        padding=padding.all(10),
                        width=250,
                        data=''
                    ),
                    Column(ref=self.task_ref)
                ]
            )
        )

        self._status_name_ref.current.value = name

        self.load_data()

    def load_data(self):
        controls = self.task_ref.current.controls
        controls.clear()

        data = storage.load_file()
        for task_name in data[self.board_name]['statuses'][self._status_name]:
            self.create_new_task(task_name)

    @property
    def name(self) -> str:
        return self._status_name

    @name.setter
    def name(self, value):
        storage.rename_status(self.board_name, self.name, value)
        self._status_name = value
        self._status_name_ref.current.value = value

    def move_task(self, e: DragTargetEvent):
        task_card = self.page.get_control(e.src_id)
        storage.change_status(
            board_name=self.board_name,
            status_name=task_card.status_name,
            task_name=task_card.name,
            new_status=self.name
        )
        e.control.create_new_task(task_card.name)
        task_card.parent.controls.remove(task_card)
        self.page.update()

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
            title=Text("Введите название!"),
            content=Column(
                [
                    dialog_text,
                    Row(
                        [
                            ft.ElevatedButton(text="Отмена", on_click=close_dlg),
                            rename_button,
                        ],
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
        storage.delete_status(self.board_name, self.name)
        parent: Row = self.parent
        parent.controls.remove(self)
        self.page.update()

    def clear(self, e):
        count = len(self.task_ref.current.controls)
        for i in range(count):
            self.task_ref.current.controls[0].delete()

    def add_task(self, e):
        def close_dlg(e):
            if (hasattr(e.control, "text") and not e.control.text == "Отмена") or (
                    type(e.control) is ft.TextField and e.control.value != ""
            ):
                storage.add_task(self.board_name, self._status_name, dialog_text.value)
                self.create_new_task(dialog_text.value)
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
            title=Text("Введите задачу!"),
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
                tight=True,
            )
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        dialog_text.focus()

    def create_new_task(self, task_name):
        new_task = TaskItem(self.board_name, self._status_name, name=task_name)
        self.task_ref.current.controls.append(new_task)


class Board(Column):
    def __init__(self, name: str):
        super().__init__()
        self._board_name = name
        self._board_name_ref = ft.Ref[Text]()
        self.alignment = ft.MainAxisAlignment.START
        self.expand = True
        self.scroll = True
        self.columns = []
        self.controls = [
            Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.TextButton("К доскам", icon=ft.icons.ARROW_BACK, on_click=self.go_to_boards),
                    Container(
                        Text(value=self._board_name, style=TextThemeStyle.HEADLINE_MEDIUM, ref=self._board_name_ref),
                        padding=padding.only(top=15)
                    ),
                    Container(
                        TextButton(
                            "Добавить новую колонку",
                            icon=icons.ADD,
                            on_click=self.add_column,
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
                ]
            ),
            Container(
                Row(
                    controls=self.columns,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    alignment=ft.MainAxisAlignment.START
                ),
            )
        ]
        self.load_data()

    def go_to_boards(self, e):
        self.page.route = '/boards'
        self.page.update()

    def load_data(self):
        self.columns.clear()
        data = storage.load_file()
        for status_name in data[self._board_name]['statuses']:
            self.create_new_column(status_name)

    @property
    def name(self) -> str:
        return self._board_name

    @name.setter
    def name(self, value):
        storage.rename_board(self._board_name, value)
        self._board_name = value
        self._board_name_ref.current.value = value

    def add_column(self, e):
        def close_dlg(e):
            if (hasattr(e.control, "text") and not e.control.text == "Отмена") or (
                    type(e.control) is ft.TextField and e.control.value != ""
            ):
                storage.add_status(self._board_name, dialog_text.value)
                self.create_new_column(dialog_text.value)
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
                tight=True,
            )
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
        dialog_text.focus()

    def create_new_column(self, column_name):
        new_column = StatusColumn(self._board_name, name=column_name)
        self.columns.append(new_column)
