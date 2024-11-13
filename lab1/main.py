import tkinter as tk
import math

size = 600
radius = 200
center = size // 2

speed = 0.01  
direction = 1 

class MovingPointApp:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(self.root, width=size, height=size, bg='white')
        self.canvas.pack()

        
        self.canvas.create_oval(center - radius, center - radius, center + radius, center + radius, outline="black", width=2)

        self.angle = 0  
        self.point = self.canvas.create_oval(0, 0, 10, 10, fill='red')
        
        self.animate()

    def animate(self):
        
        x = center + radius * math.cos(self.angle)
        y = center + radius * math.sin(self.angle)
        
        self.canvas.coords(self.point, x - 5, y - 5, x + 5, y + 5)

        self.angle += direction * speed

        self.root.after(10, self.animate)

def change_speed(new_speed, new_direction):
    global speed, direction
    speed = new_speed
    direction = new_direction

root = tk.Tk()
app = MovingPointApp(root)

root.after(2000, lambda: change_speed(0.05, -1))

root.mainloop()
