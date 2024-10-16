import sys
import random
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
import json

class RainDrop:
    def __init__(self, x, y):
        self.width = random.uniform(1, 3)  # Рандомная толщина
        self.x = x
        self.y = y
        self.height = 30  # Фиксированная высота капли
        self.opacity = random.uniform(0.5, 1.0)  # Прозрачность
        self.color = QColor("blue")

    def fall(self, speed_min, speed_max, angle_min, angle_max):
        self.x += random.uniform(angle_min, angle_max)  # Смещение по X согласно углу
        self.y += random.uniform(speed_min, speed_max)  # Смещение по Y с вариацией скорости

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)  # Установка фиксированного размера окна

        self.load_config()

        # Список для капель дождя
        self.rains = []

        # Таймеры
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_rains_pads_position)
        self.update_timer.start(5)  # Обновление положения капель каждые 40 мс

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_rains_pads)
        self.schedule_next_spawn()  # Устанавливаем рандомный таймер для спавна капель

    def load_config(self):
        try:
            with open("config.json", "r") as file:
                config = json.load(file)
                self.fall_speed_min = config["fall_speed_min"]
                self.fall_speed_max = config["fall_speed_max"]
                self.max_rains = config["max_rains"]
                self.angle_min = config["angle_min"]
                self.angle_max = config["angle_max"]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Ошибка при загрузке конфигурации: {e}")
            # Установить значения по умолчанию, если файл не найден или некорректный
            self.fall_speed_min = 9
            self.fall_speed_max = 14
            self.max_rains = 20
            self.angle_min = -1
            self.angle_max = 2

    def schedule_next_spawn(self):
        random_interval = random.randint(0, 5)  # Случайный интервал между спавнами (100-1000 мс)
        self.spawn_timer.start(random_interval)

    def update_rains_pads_position(self):
        for rain in self.rains:
            rain.fall(self.fall_speed_min, self.fall_speed_max, self.angle_min, self.angle_max)

        # Удаление капель, вышедших за пределы окна
        self.rains = [rain for rain in self.rains if rain.y < self.height()]

        self.update()  # Обновляем экран для перерисовки
        print(len(self.rains))

    def spawn_rains_pads(self):
        number_of_rains = random.randint(1, self.max_rains)  # Случайное количество капель

        for _ in range(number_of_rains):
            x = random.randint(0, self.width())  # Случайная позиция по оси X
            y = 0  # Начальное положение по оси Y (сверху)
            rain = RainDrop(x, y)
            self.rains.append(rain)

        self.schedule_next_spawn()  # Планируем следующий спавн с новым случайным интервалом

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for rain in self.rains:
            painter.setOpacity(rain.opacity)  # Устанавливаем прозрачность капли
            painter.setBrush(QBrush(rain.color))  # Устанавливаем цвет
            # Приводим значения к int для корректной отрисовки
            painter.drawRect(int(rain.x - rain.width // 2), int(rain.y), int(rain.width), int(rain.height))  # Рисуем прямоугольную каплю

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())