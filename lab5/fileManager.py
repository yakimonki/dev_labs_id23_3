import os
import shutil
from settings import WORKING_DIRECTORY


class FileManager:
    def __init__(self):
        self.current_directory = WORKING_DIRECTORY

    def _validate_path(self, path):
        return os.path.abspath(path).startswith(WORKING_DIRECTORY)

    def create_folder(self, folder_name):
        path = os.path.join(self.current_directory, folder_name)
        if not self._validate_path(path):
            print("Ошибка: Выход за пределы рабочей папки.")
            return
        try:
            os.mkdir(path)
            print(f"Папка '{folder_name}' создана.")
        except FileExistsError:
            print(f"Папка '{folder_name}' уже существует.")

    def delete_folder(self, folder_name):
        path = os.path.join(self.current_directory, folder_name)
        if not self._validate_path(path):
            print("Ошибка: Выход за пределы рабочей папки.")
            return
        try:
            os.rmdir(path)
            print(f"Папка '{folder_name}' удалена.")
        except FileNotFoundError:
            print(f"Папка '{folder_name}' не найдена.")
        except OSError:
            print(f"Папка '{folder_name}' не пуста.")

    def change_directory(self, folder_name):
        new_path = os.path.join(self.current_directory, folder_name)
        if not self._validate_path(new_path):
            print("Ошибка: Выход за пределы рабочей папки.")
            return
        if os.path.isdir(new_path):
            self.current_directory = new_path
            print(f"Перешли в папку '{folder_name}'.")
        else:
            print(f"Папка '{folder_name}' не найдена.")

    def go_up(self):
        if self.current_directory != WORKING_DIRECTORY:
            self.current_directory = os.path.dirname(self.current_directory)
            print("Поднялись на уровень вверх.")
        else:
            print("Вы уже в корневой папке.")

    def create_file(self, file_name):
        path = os.path.join(self.current_directory, file_name)
        if not self._validate_path(path):
            print("Ошибка: Выход за пределы рабочей папки.")
            return
        try:
            open(path, 'w').close()
            print(f"Файл '{file_name}' создан.")
        except FileExistsError:
            print(f"Файл '{file_name}' уже существует.")

    def write_to_file(self, file_name, text):
        path = os.path.join(self.current_directory, file_name)
        if not self._validate_path(path):
            print("Ошибка: Выход за пределы рабочей папки.")
            return
        try:
            with open(path, 'w') as file:
                file.write(text)
            print(f"Текст записан в файл '{file_name}'.")
        except FileNotFoundError:
            print(f"Файл '{file_name}' не найден.")

    def read_file(self, file_name):
        path = os.path.join(self.current_directory, file_name)
        if not self._validate_path(path):
            print("Ошибка: Выход за пределы рабочей папки.")
            return
        try:
            with open(path, 'r') as file:
                print(f"Содержимое файла '{file_name}':\n{file.read()}")
        except FileNotFoundError:
            print(f"Файл '{file_name}' не найден.")

    def delete_file(self, file_name):
        path = os.path.join(self.current_directory, file_name)
        if not self._validate_path(path):
            print("Ошибка: Выход за пределы рабочей папки.")
            return
        try:
            os.remove(path)
            print(f"Файл '{file_name}' удален.")
        except FileNotFoundError:
            print(f"Файл '{file_name}' не найден.")

    def copy_file(self, file_name, destination_folder):
        src_path = os.path.join(self.current_directory, file_name)
        dest_path = os.path.join(self.current_directory, destination_folder, file_name)
        if not self._validate_path(src_path) or not self._validate_path(dest_path):
            print("Ошибка: Выход за пределы рабочей папки.")
            return
        try:
            shutil.copy(src_path, dest_path)
            print(f"Файл '{file_name}' скопирован в папку '{destination_folder}'.")
        except FileNotFoundError:
            print(f"Файл '{file_name}' или папка '{destination_folder}' не найдены.")

    def move_file(self, file_name, destination_folder):
        src_path = os.path.join(self.current_directory, file_name)
        dest_path = os.path.join(self.current_directory, destination_folder, file_name)
        if not self._validate_path(src_path) or not self._validate_path(dest_path):
            print("Ошибка: Выход за пределы рабочей папки.")
            return
        try:
            shutil.move(src_path, dest_path)
            print(f"Файл '{file_name}' перемещен в папку '{destination_folder}'.")
        except FileNotFoundError:
            print(f"Файл '{file_name}' или папка '{destination_folder}' не найдены.")

    def rename_file(self, old_name, new_name):
        old_path = os.path.join(self.current_directory, old_name)
        new_path = os.path.join(self.current_directory, new_name)
        if not self._validate_path(old_path) or not self._validate_path(new_path):
            print("Ошибка: Выход за пределы рабочей папки.")
            return
        try:
            os.rename(old_path, new_path)
            print(f"Файл '{old_name}' переименован в '{new_name}'.")
        except FileNotFoundError:
            print(f"Файл '{old_name}' не найден.")
