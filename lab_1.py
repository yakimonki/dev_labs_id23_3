import tkinter as tk
import math


root = tk.Tk()
root.title("Движущаяся точка по окружности")

WIDTH, HEIGHT = 600, 600
CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2
RADIUS = 200

angle = 0
speed = 0.05

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
canvas.pack()

canvas.create_oval(CENTER_X - RADIUS, CENTER_Y - RADIUS,
                   CENTER_X + RADIUS, CENTER_Y + RADIUS, outline="blue", width=2)

point = canvas.create_oval(CENTER_X, CENTER_Y, CENTER_X + 10, CENTER_Y + 10, fill="red")


def move_point():
    global angle
    x = CENTER_X + RADIUS * math.cos(angle)
    y = CENTER_Y + RADIUS * math.sin(angle)

    canvas.coords(point, x - 5, y - 5, x + 5, y + 5)

    angle += speed

    root.after(10, move_point)


move_point()

root.mainloop()
