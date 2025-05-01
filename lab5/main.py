from fileManager import FileManager


def main():
    fm = FileManager()
    while True:
        print(f"\nТекущая папка: {fm.current_directory}")
        print("1. Создать папку")
        print("2. Удалить папку")
        print("3. Перейти в папку")
        print("4. Подняться на уровень вверх")
        print("5. Создать файл")
        print("6. Записать текст в файл")
        print("7. Просмотреть содержимое файла")
        print("8. Удалить файл")
        print("9. Скопировать файл")
        print("10. Переместить файл")
        print("11. Переименовать файл")
        print("12. Выйти")

        choice = input("Выберите действие: ")

        if choice == '1':
            folder_name = input("Введите имя папки: ")
            fm.create_folder(folder_name)
        elif choice == '2':
            folder_name = input("Введите имя папки: ")
            fm.delete_folder(folder_name)
        elif choice == '3':
            folder_name = input("Введите имя папки: ")
            fm.change_directory(folder_name)
        elif choice == '4':
            fm.go_up()
        elif choice == '5':
            file_name = input("Введите имя файла: ")
            fm.create_file(file_name)
        elif choice == '6':
            file_name = input("Введите имя файла: ")
            text = input("Введите текст: ")
            fm.write_to_file(file_name, text)
        elif choice == '7':
            file_name = input("Введите имя файла: ")
            fm.read_file(file_name)
        elif choice == '8':
            file_name = input("Введите имя файла: ")
            fm.delete_file(file_name)
        elif choice == '9':
            file_name = input("Введите имя файла: ")
            destination_folder = input("Введите имя папки назначения: ")
            fm.copy_file(file_name, destination_folder)
        elif choice == '10':
            file_name = input("Введите имя файла: ")
            destination_folder = input("Введите имя папки назначения: ")
            fm.move_file(file_name, destination_folder)
        elif choice == '11':
            old_name = input("Введите текущее имя файла: ")
            new_name = input("Введите новое имя файла: ")
            fm.rename_file(old_name, new_name)
        elif choice == '12':
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
