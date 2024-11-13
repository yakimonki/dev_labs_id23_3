import tkinter as tk
import random

NUM_POLES = 5          
MAX_BIRDS_ON_POLE = 3  
NUM_BIRDS = 50      
POLE_REPAIR_INTERVAL = 5000  
BIRD_SITTING_MIN = 3000     
BIRD_SITTING_MAX = 6000     
BIRD_SPEED = 5              

class Bird:
    def __init__(self, canvas, poles):
        self.canvas = canvas
        self.poles = poles
        self.sitting_time = random.randint(BIRD_SITTING_MIN, BIRD_SITTING_MAX)
        self.current_pole = None
        self.oval = canvas.create_oval(0, 0, 20, 20, fill='red')
        self.x = random.randint(50, 550)
        self.y = random.randint(50, 250)
        self.canvas.coords(self.oval, self.x - 10, self.y - 10, self.x + 10, self.y + 10)
        self.dx = random.choice([-1, 1]) * BIRD_SPEED
        self.dy = random.choice([-1, 1]) * BIRD_SPEED
        self.flying = True
        self.fly()

    def fly(self):
        if self.flying:
            self.x += self.dx
            self.y += self.dy
            if self.x < 0 or self.x > 600:
                self.dx = -self.dx
            if self.y < 0 or self.y > 400:
                self.dy = -self.dy
            self.canvas.coords(self.oval, self.x - 10, self.y - 10, self.x + 10, self.y + 10)
            self.check_near_pole()
            self.canvas.after(50, self.fly)

    def check_near_pole(self):
        for pole in self.poles:
            if pole.is_standing and len(pole.birds) < MAX_BIRDS_ON_POLE:
                if abs(self.x - pole.x) < 30 and abs(self.y - pole.y) < 50:
                    self.sit_on_pole(pole)
                    return

    def sit_on_pole(self, pole):
        self.flying = False
        self.current_pole = pole
        if self not in pole.birds:
            pole.birds.append(self)
        platform_index = len(pole.birds) - 1
        self.canvas.coords(self.oval, pole.x - 10, pole.y - 30 - platform_index * 30, pole.x + 10, pole.y - 10 - platform_index * 30)
        self.canvas.after(self.sitting_time, self.fly_away)
        pole.check_collapse()  

    def fly_away(self):
        if self.current_pole:
            if self in self.current_pole.birds:
                self.current_pole.birds.remove(self)
            self.current_pole = None
        self.flying = True
        self.dx = random.choice([-1, 1]) * BIRD_SPEED
        self.dy = random.choice([-1, 1]) * BIRD_SPEED
        self.fly()

class Pole:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.is_standing = True
        self.birds = []
        self.rect = canvas.create_rectangle(x - 10, y, x + 10, y + 100, fill='grey')
        self.platforms = [self.canvas.create_rectangle(x - 20, y - 30 - i * 30, x + 20, y - 10 - i * 30, fill='brown') for i in range(MAX_BIRDS_ON_POLE)]
        self.collapse_timer = None  

    def check_collapse(self):
        if len(self.birds) >= MAX_BIRDS_ON_POLE and self.is_standing:
            if not self.collapse_timer:  
                self.collapse_timer = self.canvas.after(1000, self.collapse)  

    def collapse(self):
        self.is_standing = False
        self.canvas.itemconfig(self.rect, fill='white')
        birds_to_fly = self.birds[:]  
        for bird in birds_to_fly:  
            bird.fly_away()  
        self.birds = []  
        self.collapse_platforms()  
        self.collapse_timer = None  

    def collapse_platforms(self):
        for platform in self.platforms:
            self.canvas.itemconfig(platform, fill='white')

    def repair(self):
        self.is_standing = True
        self.canvas.itemconfig(self.rect, fill='grey')
        for platform in self.platforms:
            self.canvas.itemconfig(platform, fill='brown')

class World:
    def __init__(self, root):
        self.canvas = tk.Canvas(root, width=600, height=400, bg='white')
        self.canvas.pack()

        self.poles = [Pole(self.canvas, x, 300) for x in range(100, 600, 100)]
        self.birds = [Bird(self.canvas, self.poles) for _ in range(NUM_BIRDS)]

        self.update_world()
        root.after(POLE_REPAIR_INTERVAL, self.repair_pole)

    def update_world(self):
        for pole in self.poles:
            if pole.is_standing:
                pole.check_collapse()
        self.canvas.after(100, self.update_world)

    def repair_pole(self):
        broken_poles = [pole for pole in self.poles if not pole.is_standing]
        if broken_poles:
            random.choice(broken_poles).repair()
        root.after(POLE_REPAIR_INTERVAL, self.repair_pole)

root = tk.Tk()

world = World(root)

root.mainloop()
