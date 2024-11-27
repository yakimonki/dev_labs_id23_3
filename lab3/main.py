import random
from tkinter import *
from tkinter import ttk
from threading import Timer
import json

# Load settings from file
try:
    with open("settings.json", 'r') as settings:
        base_settings = json.load(settings)
except FileNotFoundError:
    base_settings = {
        'BIRDS_COUNT': 5,
        'PILLARS_DURABILITY': 2,
        'PILLAR_SPAWN_INTERVAL': 5,
        'BIRD_SPAWN_INTERVAL': 2000,
        'PILLAR_SPAWN_INTERVAL': 20000,
    }
    with open('settings.json', 'w') as settings:
        json.dump(base_settings, settings)

class MainCanvas(Canvas):

    def __init__(self, root: Tk):
        super().__init__(root, width=500, height=500)
        self.pack()

class Pillar:
    def __init__(self, canvas: MainCanvas, max_birds: int, recovery_time: int, x: int, y: int, width, h):
        self.max_birds = max_birds
        self.canvas = canvas
        self.recovery_time = recovery_time
        self.count_birds = 0
        self.x = x
        self.break_pillar_flag = False
        self.y = y
        self.post_id = None
        self.beam_id = None
        self.is_fixed = True
        self.width = 20
        self.h = 10
        self.check_birds()

    def contains(self, x, y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.h

    def draw(self):
        self.post_id = self.canvas.create_rectangle(self.x, self.y, self.x + 10, self.y + 200, fill='gray',
                                                    outline='gray')
        self.beam_id = self.canvas.create_rectangle(self.x - 30, self.y, self.x + 40, self.y + 10, fill='gray',
                                                    outline='gray')

    def increase_birds_count(self):
        self.count_birds += 1

    def decrease_birds_count(self):
        self.count_birds -= 1

    def break_pillar(self):
        if not self.break_pillar_flag:
            self.canvas.itemconfigure(self.beam_id, state='hidden')
            self.canvas.itemconfigure(self.post_id, state='hidden')
            self.is_fixed = False
            self.break_pillar_flag = True
            timer = Timer(self.recovery_time, self.fix_pillar)
            timer.start()

    def fix_pillar(self):
        self.canvas.itemconfigure(self.beam_id, state='normal')
        self.canvas.itemconfigure(self.post_id, state='normal')
        self.is_fixed = True
        self.break_pillar_flag = False

    def check_birds(self):
        if self.is_fixed:
            if self.count_birds >= self.max_birds:
                self.break_pillar()

        self.canvas.after(100, self.check_birds)

class Bird:
    def __init__(self, canvas: MainCanvas, sitting_time: int, pillars: [Pillar]): # type: ignore
        self.is_leave = False
        self.leave_timer = None
        self.sitting_time = sitting_time
        self.canvas = canvas
        self.x = random.randint(50, 550)
        self.y = random.randint(50, 250)
        self.animation_progress = False
        self.bird_id = None
        self.is_can_fly = True
        self.pillars = pillars
        self.current_pillar = None

    def draw(self):
        self.bird_id = self.canvas.create_oval(0, 0, 20, 20, fill='red')
        self.canvas.coords(self.bird_id, self.x - 10, self.y - 10, self.x + 10, self.y + 10)

    def animation(self, x, y, on_animation_ended=None):
        self.is_can_fly = False
        if not self.animation_progress:
            self.animation_progress = True
            dx = x - self.x
            dy = y - self.y
            self.x = x
            self.y = y
            length = (dx ** 2 + dy ** 2) ** .5
            step = 10
            step_x = step / length * dx
            step_y = step / length * dy

            progress = 0

            def animate():
                nonlocal progress
                progress += step
                if progress < length:
                    self.canvas.move(self.bird_id, step_x, step_y)
                    self.canvas.after(40, animate)
                else:
                    self.canvas.coords(self.bird_id, x - 10, y - 10, x + 10, y + 10)
                    self.animation_progress = False
                    if self.current_pillar is None and not self.is_leave:
                        self.is_can_fly = True
                        if self.can_seat():
                            self.choose_random_pillar()
                        else:
                            self.fly()
                    if on_animation_ended is not None:
                        on_animation_ended()

            animate()

    def can_seat(self):
        return any([pillar.is_fixed for pillar in self.pillars])

    def is_pillar_broken(self):
        if not self.current_pillar.is_fixed:
            if self.leave_timer is not None:
                self.leave_timer.cancel()
            self.is_can_fly = True
            self.fly_away()
            self.current_pillar = None
        elif self.current_pillar is not None:
            self.canvas.after(100, self.is_pillar_broken)

    def fly_away(self):
        self.fly()
        self.current_pillar.decrease_birds_count()

    def leave(self):
        self.is_leave = True
        self.is_can_fly = True

        self.animation(*random.choice([[i, -10] for i in range(-10, 500, 10)]))

    def choose_random_pillar(self):
        available_pillars = list(filter(lambda x: x.is_fixed, self.pillars))
        self.current_pillar = available_pillars[random.randint(0, len(available_pillars) - 1)]
        if self.current_pillar.is_fixed:
            self.is_can_fly = False

            def on_animation():
                self.current_pillar.increase_birds_count()
                self.leave_timer = Timer(self.sitting_time, self.leave)
                self.leave_timer.start()
                self.is_pillar_broken()

            self.animation(
                random.randrange(self.current_pillar.x - 30, self.current_pillar.x + 30, random.randint(1, 10)),
                self.current_pillar.y, on_animation_ended=on_animation)
        else:
            self.current_pillar = None
            self.fly()

    def fly(self):
        if self.is_can_fly and not self.is_leave:
            x = random.randint(10, 490)
            y = random.randint(10, 240)

            def on_animation():
                self.canvas.after(50, self.fly)

            self.animation(x, y, on_animation_ended=on_animation)


class BirdPillarApp:
    def __init__(self, root):
        self.root = root
        self.root.maxsize(500, 600)
        self.root.minsize(500, 600)

        self.canvas = MainCanvas(root)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Object lists and timers
        self.pillars = []
        self.birds = []
        self.bird_spawn_interval = base_settings['BIRD_SPAWN_INTERVAL']
        self.pillar_spawn_interval = base_settings['PILLAR_SPAWN_INTERVAL']
        self.bird_spawn_timer = None
        self.pillar_spawn_timer = None

        # Create interface
        self.create_controls()

        # Initialize objects
        self.initialize_pillars()
        self.initialize_birds()
        self.start_bird_spawning()
        self.start_pillar_spawning()

    def create_controls(self):
        pillars_control_frame = Frame(self.root)
        pillars_control_frame.pack(side=BOTTOM, fill=X, pady=10)
        birds_control_frame = Frame(self.root)
        birds_control_frame.pack(side=TOP, fill = X, pady = 10)

        # Pillar durability slider
        Label(pillars_control_frame, text="Pillar Durability:").pack(side=LEFT, padx=5)
        self.pillar_durability_slider = Scale(pillars_control_frame, from_=1, to=20, orient=HORIZONTAL)
        self.pillar_durability_slider.set(base_settings['PILLARS_DURABILITY'])
        self.pillar_durability_slider.pack(side=LEFT, padx=5)

        # Pillar spawn interval
        Label(pillars_control_frame, text="Pillar Spawn Interval (ms):").pack(side=LEFT, padx=5)
        self.pillar_spawn_interval_box = Spinbox(pillars_control_frame, from_=1000, to=10000, increment=500, width=5, command=self.update_pillar_spawn_interval)
        self.pillar_spawn_interval_box.pack(side=LEFT, padx=5)
        self.pillar_spawn_interval_box.delete(0, END)
        self.pillar_spawn_interval_box.insert(0, self.pillar_spawn_interval)

        # Bird spawn interval
        Label(birds_control_frame, text="Bird Spawn Interval (ms):").pack(side=LEFT, padx=5)
        self.bird_spawn_interval_box = Spinbox(birds_control_frame, from_=500, to=20000, increment=100, width=5, command=self.update_bird_spawn_interval)
        self.bird_spawn_interval_box.pack(side=LEFT, padx=5)
        self.bird_spawn_interval_box.delete(0, END)
        self.bird_spawn_interval_box.insert(0, self.bird_spawn_interval)

        

    def start_bird_spawning(self):
        """Start bird spawning timer."""
        if self.bird_spawn_timer:
            self.root.after_cancel(self.bird_spawn_timer)
        self.bird_spawn_timer = self.root.after(self.bird_spawn_interval, self.spawn_bird)

    def spawn_bird(self):
        """Spawn a new bird."""
        bird = Bird(self.canvas, random.randint(1, 6), self.pillars)
        self.birds.append(bird)
        bird.draw()
        bird.fly()
        self.start_bird_spawning()

    def update_bird_spawn_interval(self):
        """Update bird spawn interval."""
        try:
            self.bird_spawn_interval = int(self.bird_spawn_interval_box.get())
            self.start_bird_spawning()
        except ValueError:
            pass

    def start_pillar_spawning(self):
        """Start pillar spawning timer."""
        if self.pillar_spawn_timer:
            self.root.after_cancel(self.pillar_spawn_timer)
        self.pillar_spawn_timer = self.root.after(self.pillar_spawn_interval, self.spawn_pillar)

    def spawn_pillar(self):
        """Spawn a new pillar."""
        x = random.randint(50, 450)
        y = random.randint(250, 450)
        new_pillar = Pillar(self.canvas, self.pillar_durability_slider.get(), base_settings['PILLAR_SPAWN_INTERVAL'], x, y, 20, 10)
        self.pillars.append(new_pillar)
        new_pillar.draw()
        self.start_pillar_spawning()

    def update_pillar_spawn_interval(self):
        """Update pillar spawn interval."""
        try:
            self.pillar_spawn_interval = int(self.pillar_spawn_interval_box.get())
            self.start_pillar_spawning()
        except ValueError:
            pass

    def on_canvas_click(self, event):
        """Handle pillar placement or editing."""
        x, y = event.x, event.y
        
        # Проверка на пересечение с другими столбами
        for pillar in self.pillars:
            if abs(pillar.x - x) < 100 and abs(pillar.y - y) < 100:  # Минимальное расстояние в 50 пикселей
                print("Too close to an existing pillar. Cannot create a new one.")
                return

        # Если столб не найден рядом, создаём новый
        new_pillar = Pillar(self.canvas, self.pillar_durability_slider.get(), base_settings['PILLAR_SPAWN_INTERVAL'], x, y, 20, 10)
        self.pillars.append(new_pillar)
        new_pillar.draw()
        print(f"Added new pillar at ({x}, {y}) with durability {new_pillar.max_birds}")

    def initialize_pillars(self):
        """Initialize default pillars."""
        self.pillars.clear()
        for i in range(4):
            pillar = Pillar(self.canvas, base_settings['PILLARS_DURABILITY'], base_settings['PILLAR_SPAWN_INTERVAL'], 70 * i + 50, 300, 20, 10)
            self.pillars.append(pillar)
            pillar.draw()

    def initialize_birds(self):
        """Initialize default birds."""
        self.birds.clear()
        for _ in range(base_settings['BIRDS_COUNT']):
            bird = Bird(self.canvas, random.randint(1, 6), self.pillars)
            self.birds.append(bird)
            bird.draw()
            bird.fly()

def main():
    root = Tk()
    root.resizable(True, True)
    app = BirdPillarApp(root)
    root.mainloop()

if __name__ == '__main__':  
    main()
