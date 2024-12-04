import sys
import random
import math
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap
from PyQt5.QtWidgets import QPushButton, QLineEdit, QSpinBox, QSlider
import json
from PyQt5.QtCore import QTimer, QDateTime
import os

os.environ["QT_SCALE_FACTOR"] = "1"  
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1" 

class Cloud:
    def __init__(self, x, y, shape, rain_density, fall_speed_min, fall_speed_max, angle_min, angle_max, width=120, height=60):
        self.x = x
        self.y = y
        self.shape = shape  
        self.width = width
        self.height = height
        self.rain_density = rain_density  
        self.fall_speed_min = fall_speed_min
        self.fall_speed_max = fall_speed_max
        self.angle_min = angle_min
        self.angle_max = angle_max
        self.rains = []  

    def draw(self, painter, selected=False):
        if self.shape == "Прямоугольник":
            painter.setBrush(QBrush(QColor(176,224,230)))
            if selected:
                pen = QPen(QColor(0, 71, 171), 1)
                painter.setPen(pen)
            else:
                painter.setPen(Qt.NoPen)
            painter.drawRect(self.x, self.y, self.width, self.height)
        elif self.shape == "Овал":
            painter.setBrush(QBrush(QColor(176,224,230)))
            if selected:
                pen = QPen(QColor(0, 71, 171), 1)
                painter.setPen(pen)
            else:
                painter.setPen(Qt.NoPen)
            painter.drawEllipse(self.x, self.y, self.width, self.height)

        elif self.shape == "Винни-Пух":
            pixmap = QPixmap('Винни_Пух.png')
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(self.width*2, self.height*2, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                new_x = self.x + (self.width - scaled_pixmap.width()) // 2
                new_y = self.y + (self.height - scaled_pixmap.height()) // 2
                painter.drawPixmap(new_x, new_y, scaled_pixmap)

                if selected:
                    path = QPainterPath()
                    path.addEllipse(new_x, new_y, scaled_pixmap.width(), scaled_pixmap.height())  # Пример: добавляем эллипс, замените на нужную форму
                    pen = QPen(QColor(0, 71, 171), 1)
                    painter.setPen(pen)
                    painter.setBrush(Qt.NoBrush)
                    painter.drawPath(path)
            else:
                print("Error: Could not load 'Винни-Пух.png'")

class RainDrop:
    def __init__(self, x, y):
        self.width = random.uniform(1, 3)  
        self.x = x
        self.y = y
        self.height = 30  
        self.opacity = random.uniform(0.5, 1.0)  
        self.color = QColor("blue")
        self.angle = 0
       
    def fall(self, speed_min, speed_max, angle_min, angle_max):
        self.angle = random.uniform(angle_min, angle_max) 
        self.x +=  -math.sin(math.radians(self.angle)) * random.uniform(speed_min, speed_max)
        self.y += math.cos(math.radians(self.angle)) * random.uniform(speed_min, speed_max)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)  

        self.config = self.load_config()

        self.clouds = []
        self.rains = []
        self.selected_cloud = None   

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_rains_pads_position)
        self.update_timer.start()

        self.spawn_timer = QTimer()
        self.spawn_timer.timeout.connect(self.spawn_rains_pads)
        self.spawn_timer.start(random.randint(500, 2000))

        self.init_ui()

    def init_ui(self):
        self.add_cloud_button = QPushButton("Добавить тучку", self)
        self.add_cloud_button.setGeometry(680, 50, 110, 50)
        self.add_cloud_button.clicked.connect(self.add_cloud)

        self.delete_cloud_button = QPushButton("Удалить тучку", self)
        self.delete_cloud_button.setGeometry(680, 200, 110, 50)
        self.delete_cloud_button.clicked.connect(self.delete_cloud)

        self.cloud_type_combo = QComboBox(self)
        self.cloud_type_combo.setGeometry(680, 125, 110, 50)
        self.cloud_type_combo.addItem("Прямоугольник")
        self.cloud_type_combo.addItem("Овал")
        self.cloud_type_combo.addItem("Винни-Пух")

        self.rain_density_label = QLabel("Плотность дождя:", self)
        self.speed_min_label = QLabel("Минимальная скорость:", self)
        self.speed_max_label = QLabel("Максимальная скорость:", self)

        self.rain_density_spin = QSpinBox(self)
        self.rain_density_spin.setValue(self.max_rains)

        self.speed_min_spin = QSpinBox(self)
        self.speed_min_spin.setValue(self.fall_speed_min)

        self.speed_max_spin = QSpinBox(self)
        self.speed_max_spin.setValue(self.fall_speed_max)

        self.rain_density_label.setGeometry(680, 180, 120, 40)
        self.speed_min_label.setGeometry(680, 280, 120, 40)
        self.speed_max_label.setGeometry(680, 380, 120, 40)

        self.speed_min_spin.valueChanged.connect(self.update_speed_parameters)
        self.speed_max_spin.valueChanged.connect(self.update_speed_parameters)
        self.rain_density_spin.valueChanged.connect(self.update_density_parameter)

        self.cloud_x_label = QLabel("X позиции:", self)
        self.cloud_x_spin = QSpinBox(self)
        self.cloud_x_spin.setRange(0, self.width())
        self.cloud_x_spin.valueChanged.connect(self.update_cloud_params)

        self.cloud_y_label = QLabel("Y позиции:", self)
        self.cloud_y_spin = QSpinBox(self)
        self.cloud_y_spin.setRange(0, self.height())
        self.cloud_y_spin.valueChanged.connect(self.update_cloud_params)

        self.cloud_width_label = QLabel("Ширина:", self)
        self.cloud_width_spin = QSpinBox(self)
        self.cloud_width_spin.setRange(10, 300)
        self.cloud_width_spin.valueChanged.connect(self.update_cloud_size)

        self.cloud_height_label = QLabel("Высота:", self)
        self.cloud_height_spin = QSpinBox(self)
        self.cloud_height_spin.setRange(10, 200)
        self.cloud_height_spin.valueChanged.connect(self.update_cloud_size)

        self.angle_min_label = QLabel("Min угол наклона:", self)
        self.angle_min_spin = QSpinBox(self)
        self.angle_min_spin.setRange(-10, 10) 
        self.angle_min_spin.setValue(self.angle_min)

        self.angle_max_label = QLabel("Max угол наклона:", self)
        self.angle_max_spin = QSpinBox(self)
        self.angle_max_spin.setRange(-10, 10)  # Задайте диапазон по вашему усмотрению
        self.angle_max_spin.setValue(self.angle_max)

        self.rain_density_spin.valueChanged.connect(self.update_cloud_params)
        self.speed_min_spin.valueChanged.connect(self.update_cloud_params)
        self.speed_max_spin.valueChanged.connect(self.update_cloud_params)

        self.cloud_x_spin.valueChanged.connect(self.update_cloud_position)
        self.cloud_y_spin.valueChanged.connect(self.update_cloud_position)

        self.angle_min_spin.valueChanged.connect(self.update_angle_parameters)
        self.angle_max_spin.valueChanged.connect(self.update_angle_parameters)


        y_offset = 200
        for i, (label, spin_box) in enumerate([
            (self.cloud_x_label, self.cloud_x_spin),
            (self.cloud_y_label, self.cloud_y_spin),
            (self.cloud_width_label, self.cloud_width_spin),
            (self.cloud_height_label, self.cloud_height_spin),
            (self.rain_density_label, self.rain_density_spin),
            (self.speed_min_label, self.speed_min_spin),
            (self.speed_max_label, self.speed_max_spin),
            (self.angle_min_label, self.angle_min_spin),
            (self.angle_max_label, self.angle_max_spin)
        ]):
            label.setGeometry(10, y_offset + i * 30, 120, 20)
            spin_box.setGeometry(140, y_offset + i * 30, 100, 20)

    def mousePressEvent(self, event):
        clicked_x, clicked_y = event.x(), event.y()
        for cloud in self.clouds:
            if cloud.x <= clicked_x <= cloud.x + cloud.width and \
            cloud.y <= clicked_y <= cloud.y + cloud.height:
                self.selected_cloud = cloud
                self.update_cloud_params()
                self.is_dragging = True  
                return

        self.selected_cloud = None
        self.is_dragging = False  
        self.update()

    def mouseMoveEvent(self, event):
        if self.is_dragging and self.selected_cloud: 
            self.selected_cloud.x = event.x() - self.selected_cloud.width // 2  
            self.selected_cloud.y = event.y() - self.selected_cloud.height // 2
            
            self.update_cloud_params()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False

    def update_cloud_params(self):
        if not hasattr(self, 'selected_cloud') or not self.selected_cloud:
            return

        self.cloud_x_spin.blockSignals(True)
        self.cloud_y_spin.blockSignals(True)
        self.cloud_width_spin.blockSignals(True)
        self.cloud_height_spin.blockSignals(True)
        self.rain_density_spin.blockSignals(True)
        self.speed_min_spin.blockSignals(True)
        self.angle_min_spin.blockSignals(True)
        self.angle_max_spin.blockSignals(True)

        self.cloud_x_spin.setValue(self.selected_cloud.x)
        self.cloud_y_spin.setValue(self.selected_cloud.y)
        self.cloud_width_spin.setValue(self.selected_cloud.width)
        self.cloud_height_spin.setValue(self.selected_cloud.height)
        self.rain_density_spin.setValue(self.selected_cloud.rain_density)
        self.speed_min_spin.setValue(self.selected_cloud.fall_speed_min)
        self.speed_max_spin.setValue(self.selected_cloud.fall_speed_max)
        self.angle_min_spin.setValue(self.selected_cloud.angle_min)
        self.angle_max_spin.setValue(self.selected_cloud.angle_max)

        self.cloud_x_spin.blockSignals(False)
        self.cloud_y_spin.blockSignals(False)
        self.cloud_width_spin.blockSignals(False)
        self.cloud_height_spin.blockSignals(False)
        self.rain_density_spin.blockSignals(False)
        self.speed_min_spin.blockSignals(False)
        self.speed_max_spin.blockSignals(False)
        self.angle_min_spin.blockSignals(False)
        self.angle_max_spin.blockSignals(False)

    def update_speed_parameters(self):
        if not hasattr(self, 'selected_cloud') or not self.selected_cloud:
            return
        
        self.selected_cloud.fall_speed_min = self.speed_min_spin.value()
        self.selected_cloud.fall_speed_max = self.speed_max_spin.value()

        for rain in self.selected_cloud.rains:
            rain.fall(self.selected_cloud.fall_speed_min, self.selected_cloud.fall_speed_max, self.selected_cloud.angle_min, self.selected_cloud.angle_max)

        self.update()

    def update_density_parameter(self):
        if not hasattr(self, 'selected_cloud') or not self.selected_cloud:
            return
        
        if self.selected_cloud:
            self.selected_cloud.rain_density = self.rain_density_spin.value()
            self.update()

    def update_cloud_position(self):
        if not hasattr(self, 'selected_cloud') or not self.selected_cloud:
            return

        if self.selected_cloud:
            self.selected_cloud.x = self.cloud_x_spin.value()
            self.selected_cloud.y = self.cloud_y_spin.value()

            self.update()

    def update_cloud_size(self):
        if not hasattr(self, 'selected_cloud') or not self.selected_cloud:
            return
        
        self.selected_cloud.width = self.cloud_width_spin.value()
        self.selected_cloud.height = self.cloud_height_spin.value()

        self.update_cloud_params()

        self.update()

    def update_angle_parameters(self):
        if not hasattr(self, 'selected_cloud') or not self.selected_cloud:
            return

        self.selected_cloud.angle_min = self.angle_min_spin.value()
        self.selected_cloud.angle_max = self.angle_max_spin.value()

        self.update_cloud_params()
        self.update() 

    def add_cloud(self):
        cloud_type = self.cloud_type_combo.currentText()
        fall_speed_min = self.fall_speed_min
        fall_speed_max = self.fall_speed_max
        rain_density = self.max_rains
        angle_min = self.angle_min
        angle_max = self.angle_max

        cloud = Cloud(
            random.randint(0, 600), random.randint(0, 100), shape=cloud_type,
            rain_density=rain_density, fall_speed_min=fall_speed_min, fall_speed_max=fall_speed_max, angle_min = angle_min, angle_max = angle_max)
        self.clouds.append(cloud)
        self.update()

    def delete_cloud(self):
        if not self.selected_cloud:
            return

        self.clouds.remove(self.selected_cloud)  
        self.selected_cloud = None 
        self.update()

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
            self.fall_speed_min = 9
            self.fall_speed_max = 14
            self.max_rains = 20
            self.angle_min = -1
            self.angle_max = 2
    
    def update_rains_pads_position(self):
        if self.selected_cloud:
            while len(self.selected_cloud.rains) < self.selected_cloud.rain_density:
                x = random.randint(self.selected_cloud.x, self.selected_cloud.x + self.selected_cloud.width)
                y = self.selected_cloud.y + self.selected_cloud.height // 2
                rain = RainDrop(x, y)
                self.selected_cloud.rains.append(rain)

            for rain in self.selected_cloud.rains:
                rain.fall(self.selected_cloud.fall_speed_min, self.selected_cloud.fall_speed_max, self.selected_cloud.angle_min, self.selected_cloud.angle_max)

            self.selected_cloud.rains = [rain for rain in self.selected_cloud.rains if rain.y < self.height()]

        for cloud in self.clouds:
            if cloud != self.selected_cloud:
                while len(cloud.rains) < cloud.rain_density:
                    x = random.randint(cloud.x, cloud.x + cloud.width)
                    y = cloud.y + cloud.height // 2
                    rain = RainDrop(x, y)
                    cloud.rains.append(rain)

                for rain in cloud.rains:
                    rain.fall(cloud.fall_speed_min, cloud.fall_speed_max, cloud.angle_min, cloud.angle_max)

                cloud.rains = [rain for rain in cloud.rains if rain.y < self.height()]

        self.update()


    def spawn_rains_pads(self):

        number_of_rains = random.randint(1, self.max_rains)
        for cloud in self.clouds: 
            for _ in range(number_of_rains):
                x = random.randint(cloud.x, cloud.x + cloud.width)
                y = cloud.y + cloud.height // 2 
                rain = RainDrop(x, y)
                cloud.rains.append(rain)

        self.spawn_timer.start(random.randint(500, 2000))  

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for cloud in self.clouds:
            cloud.draw(painter, selected=(cloud == self.selected_cloud))
            for rain in cloud.rains:
                painter.save() 
                painter.translate(rain.x, rain.y)  
                painter.rotate(rain.angle) 
                painter.setBrush(QBrush(rain.color))
                painter.drawRect(int(-rain.width // 2), 0, int(rain.width), int(rain.height))  
                painter.restore() 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
