import json
from os import PathLike

from exceptions import BoardAlreadyExist, BoardNotExist, StatusAlreadyExist, StatusNotExist, TaskAlreadyExist, TaskNotExist


class Storage:
    def __init__(self, path: PathLike[str] = 'data/data.json'):
        self.path = path

    @staticmethod
    def create_file(path='data/data.json') -> None:
        with open(path, 'w') as file:
            file.write('{}')

    def load_file(self) -> dict:
        with open(self.path, 'r') as file:
            return json.loads(file.read())

    def save_file(self, data: dict) -> None:
        with open(self.path, 'w') as file:
            file.write(json.dumps(data))


class BoardStorage(Storage):
    def add_board(self, name: str) -> None:
        data = self.load_file()

        if name in data:
            raise BoardAlreadyExist(f'Board {name} already exist')

        data[name] = {
            'statuses': {}
        }
        self.save_file(data)

    def delete_board(self, board_name: str) -> None:
        data = self.load_file()

        board = data.get(board_name)
        if board is None:
            raise BoardNotExist(f'Board {board_name} not exist')

        del data[board_name]
        self.save_file(data)

    def rename_board(self, board_name: str, new_board_name: str):
        data = self.load_file()

        board = data.get(board_name)
        if board is None:
            raise BoardNotExist(f'Board {board_name} not exist')

        data[new_board_name] = data.pop(board_name)

        self.save_file(data)


class StatusStorage(Storage):
    def add_status(self, board_name: str, status_name: str) -> None:
        data = self.load_file()
        board = data.get(board_name)
        if board is None:
            raise BoardNotExist(f'Board {board_name} not exist')

        if status_name in board['statuses']:
            raise StatusAlreadyExist(f'Task {status_name} already exist')
        board['statuses'][status_name] = []
        self.save_file(data)

    def delete_status(self, board_name: str, status_name: str) -> None:
        data = self.load_file()

        board = data.get(board_name)
        if board is None:
            raise BoardNotExist(f'Board {board_name} not exist')

        status = board['statuses'].get(status_name)
        if status is None:
            raise StatusNotExist(f'Status {status_name} not exist')

        del board['statuses'][status_name]
        self.save_file(data)

    def rename_status(self, board_name: str, status_name: str, new_status: str):
        data = self.load_file()

        board = data.get(board_name)
        if board is None:
            raise BoardNotExist(f'Board {board_name} not exist')

        status = board['statuses'].get(status_name)
        if status is None:
            raise StatusNotExist(f'Status {status_name} not exist')
        board['statuses'][new_status] = board['statuses'].pop(status_name)

        self.save_file(data)


class TaskStorage(Storage):
    def add_task(self, board_name: str, status_name: str, task_name: str) -> None:
        data = self.load_file()

        board = data.get(board_name)
        if board is None:
            raise BoardNotExist(f'Board {board_name} not exist')

        status = board['statuses'].get(status_name)
        if status is None:
            raise StatusNotExist(f'Status {status_name} not exist')
        if task_name in status:
            raise TaskAlreadyExist(f'Status {task_name} not exist')

        status.append(task_name)
        self.save_file(data)

    def delete_task(self, board_name: str, status_name: str, task_name: str) -> None:
        data = self.load_file()

        board = data.get(board_name)
        if board is None:
            raise BoardNotExist(f'Board {board_name} not exist')

        status = board['statuses'].get(status_name)
        if status is None:
            raise StatusNotExist(f'Status {status_name} not exist')
        if task_name not in status:
            raise TaskNotExist(f'Status {task_name} not exist')

        status.remove(task_name)
        self.save_file(data)

    def rename_task(self, board_name: str, status_name: str, task_name: str, new_name: str):
        data = self.load_file()

        board = data.get(board_name)
        if board is None:
            raise BoardNotExist(f'Board {board_name} not exist')

        status = board['statuses'].get(status_name)
        if status is None:
            raise StatusNotExist(f'Status {status_name} not exist')
        if task_name not in status:
            raise TaskNotExist(f'Status {task_name} not exist')

        status.remove(task_name)
        status.append(new_name)
        self.save_file(data)

    def change_status(self, board_name: str, status_name: str, task_name: str, new_status: str):
        data = self.load_file()

        board = data.get(board_name)
        if board is None:
            raise BoardNotExist(f'Board {board_name} not exist')

        status = board['statuses'].get(status_name)
        if status is None:
            raise StatusNotExist(f'Status {status_name} not exist')
        if task_name not in status:
            raise TaskNotExist(f'Status {task_name} not exist')

        status.remove(task_name)
        self.save_file(data)
        self.add_task(board_name, new_status, task_name)


class StorageMixin(BoardStorage, StatusStorage, TaskStorage):
    ...


storage = StorageMixin()
