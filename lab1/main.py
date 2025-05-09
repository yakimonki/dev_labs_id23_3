#!/usr/bin/env python
# coding: utf-8

# In[2]:


import tkinter as tk


# In[3]:


from tkinter import *
from tkinter import colorchooser
from random import *
import math


# In[10]:


window = Tk()
colorchooser.askcolor()

size = 600
root = Tk()
canvas = Canvas(root, width=size, height=size)
canvas.pack()
diapason = 0


# In[ ]:


while diapason < 1000:
    colors = choice(['aqua', 'blue', 'fuchsia', 'green', 'maroon', 'orange',
                  'pink', 'purple', 'red','yellow', 'violet', 'indigo', 'chartreuse', 'lime'])
    x0 = randint(0, size)
    y0 = randint(0, size)
    d = randint(0, size/5)
    canvas.create_oval(x0, y0, x0+d, y0+d, fill=colors)
    root.update()
    diapason += 1


# In[5]:


class MovingPointApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Moving Point on a Circle")
        self.canvas = tk.Canvas(self.root, width=600, height=600, bg="white")
        self.canvas.pack()

        # Параметры окружности
        self.circle_radius = 200
        self.circle_center = (300, 300)
        self.speed = 0.01  # скорость движения
        self.angle = 0  # начальный угол

        # Рисуем окружность
        self.canvas.create_oval(
            self.circle_center[0] - self.circle_radius,
            self.circle_center[1] - self.circle_radius,
            self.circle_center[0] + self.circle_radius,
            self.circle_center[1] + self.circle_radius
        )

        # Создаем точку
        self.point = self.canvas.create_oval(0, 0, 10, 10, fill="red")

        # Кнопки для изменения скорости и направления
        tk.Button(self.root, text="Увеличить скорость", command=self.increase_speed).pack(side=tk.LEFT)
        tk.Button(self.root, text="Уменьшить скорость", command=self.decrease_speed).pack(side=tk.LEFT)
        tk.Button(self.root, text="Сменить направление", command=self.change_direction).pack(side=tk.LEFT)

        # Запуск анимации
        self.animate()

    def increase_speed(self):
        self.speed += 0.005

    def decrease_speed(self):
        if self.speed > 0.005:  # Ограничим минимальную скорость
            self.speed -= 0.005

    def change_direction(self):
        self.speed = -self.speed

    def animate(self):
        # Вычисляем координаты точки на окружности
        x = self.circle_center[0] + self.circle_radius * math.cos(self.angle)
        y = self.circle_center[1] + self.circle_radius * math.sin(self.angle)

        # Обновляем позицию точки
        self.canvas.coords(self.point, x - 5, y - 5, x + 5, y + 5)
        '''Чтобы сделать точку визуально круглой, добавляется и вычитается 5 пикселей (половина ширины/высоты точки), 
        чтобы точка оставалась небольшой (10x10 пикселей) и располагалась точно по центру в координатах (x, y)'''

        # Изменяем угол для следующего шага
        self.angle += self.speed

        # Перезапускаем анимацию через 10 мс
        self.root.after(10, self.animate)

# Создаем окно
root = tk.Tk()
app = MovingPointApp(root)
root.mainloop()


# In[ ]:




