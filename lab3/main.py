import random
from tkinter import *
from tkinter import ttk
from threading import Timer
import json

try:
    with open("settings.json", 'r') as config_file:
        default_config = json.load(config_file)
except FileNotFoundError:
    default_config = {
        'BIRD_COUNT': 5,
        'PILLAR_STRENGTH': 2,
        'BIRD_SPAWN_DELAY': 2000,
        'PILLAR_REPAIR_DELAY': 20000,
    }
    with open('settings.json', 'w') as config_file:
        json.dump(default_config, config_file)

class GameCanvas(Canvas):

    def __init__(self, root: Tk):
        super().__init__(root, width=500, height=400)
        self.pack()

class SupportPillar:
    def __init__(self, canvas: GameCanvas, max_load: int, repair_delay: int, x_coord: int, y_coord: int, base_width, height):
        self.is_paused = False
        self.max_load = max_load
        self.canvas = canvas
        self.repair_delay = repair_delay
        self.current_load = 0
        self.x_coord = x_coord
        self.is_broken = False
        self.y_coord = y_coord
        self.column_id = None
        self.crossbeam_id = None
        self.is_intact = True
        self.base_width = 20
        self.height = 10
        self.monitor_load()

    def is_within_bounds(self, x_coord, y_coord):
        return (self.x_coord - 10 <= x_coord <= self.x_coord + self.base_width + 10) and (self.y_coord <= y_coord <= self.y_coord + 200)

    def render(self):
        self.column_id = self.canvas.create_rectangle(self.x_coord, self.y_coord, self.x_coord + 10, self.y_coord + 200, fill='gray', outline='gray')
        self.crossbeam_id = self.canvas.create_rectangle(self.x_coord - 30, self.y_coord, self.x_coord + 40, self.y_coord + 10, fill='gray', outline='gray')

    def increment_load(self):
        self.current_load += 1

    def decrement_load(self):
        self.current_load -= 1

    def collapse(self):
        if not self.is_broken:
            self.canvas.itemconfigure(self.crossbeam_id, state='hidden')
            self.canvas.itemconfigure(self.column_id, state='hidden')
            self.is_intact = False
            self.is_broken = True
            repair_timer = Timer(self.repair_delay, self.repair)
            repair_timer.start()

    def repair(self):
        self.canvas.itemconfigure(self.crossbeam_id, state='normal')
        self.canvas.itemconfigure(self.column_id, state='normal')
        self.is_intact = True
        self.is_broken = False

    def monitor_load(self):
        if self.is_paused:
            return
        if self.is_intact:
            if self.current_load >= self.max_load:
                self.collapse()
        self.canvas.after(100, self.monitor_load)

class FlyingBird:
    def __init__(self, canvas: GameCanvas, perch_time: int, pillars: [SupportPillar]): 
        self.has_left = False
        self.leave_timer = None
        self.perch_time = perch_time
        self.canvas = canvas
        self.x_coord = random.randint(50, 550)
        self.y_coord = random.randint(50, 250)
        self.in_animation = False
        self.bird_id = None
        self.is_flying = True
        self.pillars = pillars
        self.current_pillar = None

    def render(self):
        self.bird_id = self.canvas.create_oval(0, 0, 20, 20, fill='red')
        self.canvas.coords(self.bird_id, self.x_coord - 10, self.y_coord - 10, self.x_coord + 10, self.y_coord + 10)

    def animate(self, x_target, y_target, on_animation_end=None):
        self.is_flying = False
        if not self.in_animation:
            self.in_animation = True
            dx = x_target - self.x_coord
            dy = y_target - self.y_coord
            self.x_coord = x_target
            self.y_coord = y_target
            distance = (dx ** 2 + dy ** 2) ** 0.5
            step_size = 10
            step_x = step_size / distance * dx
            step_y = step_size / distance * dy

            progress = 0

            def perform_animation():
                nonlocal progress
                progress += step_size
                if progress < distance:
                    self.canvas.move(self.bird_id, step_x, step_y)
                    self.canvas.after(40, perform_animation)
                else:
                    self.canvas.coords(self.bird_id, x_target - 10, y_target - 10, x_target + 10, y_target + 10)
                    self.in_animation = False
                    if self.current_pillar is None and not self.has_left:
                        self.is_flying = True
                        if self.can_perch():
                            self.select_random_pillar()
                        else:
                            self.fly_randomly()
                    if on_animation_end is not None:
                        on_animation_end()

            perform_animation()

    def can_perch(self):
        return any([pillar.is_intact for pillar in self.pillars])

    def check_pillar_status(self):
        if not self.current_pillar.is_intact:
            if self.leave_timer is not None:
                self.leave_timer.cancel()
            self.is_flying = True
            self.depart_pillar()
            self.current_pillar = None
        elif self.current_pillar is not None:
            self.canvas.after(100, self.check_pillar_status)

    def depart_pillar(self):
        self.fly_randomly()
        self.current_pillar.decrement_load()

    def leave(self):
        self.has_left = True
        self.is_flying = True

        self.animate(*random.choice([[coord, -10] for coord in range(-10, 500, 10)]))

    def select_random_pillar(self):
        intact_pillars = list(filter(lambda p: p.is_intact, self.pillars))
        self.current_pillar = intact_pillars[random.randint(0, len(intact_pillars) - 1)]
        if self.current_pillar.is_intact:
            self.is_flying = False

            def on_animation_done():
                self.current_pillar.increment_load()
                self.leave_timer = Timer(self.perch_time, self.leave)
                self.leave_timer.start()
                self.check_pillar_status()

            self.animate(
                random.randrange(self.current_pillar.x_coord - 30, self.current_pillar.x_coord + 30, random.randint(1, 10)),
                self.current_pillar.y_coord, on_animation_end=on_animation_done)
        else:
            self.current_pillar = None
            self.fly_randomly()

    def fly_randomly(self):
        if self.is_flying and not self.has_left:
            x_target = random.randint(10, 490)
            y_target = random.randint(10, 240)

            def on_animation_end():
                self.canvas.after(50, self.fly_randomly)

            self.animate(x_target, y_target, on_animation_end=on_animation_end)



class BirdPillarGame:
    def __init__(self, root):
        self.is_paused = False  
        self.pause_button = Button(root, text="Pause", command=self.toggle_game_pause)
        self.pause_button.pack(side=TOP, pady=5)

        self.root = root
        self.root.maxsize(600, 700)
        self.root.minsize(600, 700)

        self.canvas = GameCanvas(root)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        self.pillars = []
        self.birds = []
        self.bird_spawn_delay = default_config['BIRD_SPAWN_DELAY']
        self.pillar_repair_delay = 5000  
        self.repair_timer = None
        self.is_animation_paused = False

        self.setup_controls()

        self.create_initial_pillars()
        self.spawn_initial_birds()
        self.start_bird_spawning()
        self.start_pillar_repair_cycle()

    def setup_controls(self):
        birds_control_frame = Frame(self.root)
        birds_control_frame.pack(side=TOP, fill=X, pady=10)
        pillars_control_frame = Frame(self.root)
        pillars_control_frame.pack(side=BOTTOM, fill=X, pady=10)

        Label(birds_control_frame, text="Bird Spawn Interval (ms):").pack(side=LEFT, padx=5)
        self.spawn_interval_box = Spinbox(birds_control_frame, from_=500, to=20000, increment=100, width=5, command=self.update_spawn_delay)
        self.spawn_interval_box.pack(side=LEFT, padx=5)
        self.spawn_interval_box.delete(0, END)
        self.spawn_interval_box.insert(0, self.bird_spawn_delay)

        Label(pillars_control_frame, text="Pillar Repair Interval (ms):").pack(side=LEFT, padx=5, pady=80)
        self.repair_interval_box = Spinbox(pillars_control_frame, from_=1000, to=30000, increment=1000, width=5, command=self.update_repair_delay)
        self.repair_interval_box.pack(side=LEFT, padx=5)
        self.repair_interval_box.delete(0, END)
        self.repair_interval_box.insert(0, self.pillar_repair_delay)

        Label(pillars_control_frame, text="Pillar Durability:").pack(side=LEFT, padx=5)
        self.durability_slider = Scale(pillars_control_frame, from_=1, to=20, orient=HORIZONTAL)
        self.durability_slider.set(default_config['PILLAR_STRENGTH'])
        self.durability_slider.pack(side=LEFT, padx=5)

    def toggle_animation(self):
        self.is_animation_paused = not self.is_animation_paused

        for bird in self.birds:
            bird.is_flying = not self.is_animation_paused
            if self.is_animation_paused:
                if bird.leave_timer:
                    bird.leave_timer.cancel()
            else:
                if not bird.has_left and bird.is_flying:
                    bird.fly_randomly()

        self.pause_button.config(text="Resume Animation" if self.is_animation_paused else "Pause Animation")

    def start_bird_spawning(self):
        if hasattr(self, 'spawn_timer') and self.spawn_timer:
            self.root.after_cancel(self.spawn_timer)
        self.spawn_timer = self.root.after(self.bird_spawn_delay, self.create_bird)

    def create_bird(self):
        if not self.is_animation_paused:
            bird = FlyingBird(self.canvas, random.randint(1, 6), self.pillars)
            self.birds.append(bird)
            bird.render()
            bird.fly_randomly()
        self.start_bird_spawning()

    def update_spawn_delay(self):
        try:
            self.bird_spawn_delay = int(self.spawn_interval_box.get())
            self.start_bird_spawning()
        except ValueError:
            pass

    def start_pillar_repair_cycle(self):
        if self.repair_timer:
            self.root.after_cancel(self.repair_timer)
        self.repair_timer = self.root.after(self.pillar_repair_delay, self.repair_pillars)

    def repair_pillars(self):
        for pillar in self.pillars:
            if not pillar.is_intact:
                pillar.max_load = self.durability_slider.get()  
                pillar.repair()
                print(f"Pillar at ({pillar.x_coord}, {pillar.y_coord}) repaired with durability {pillar.max_load}.")
        self.start_pillar_repair_cycle()

    def update_repair_delay(self):
        try:
            self.pillar_repair_delay = int(self.repair_interval_box.get())
            self.start_pillar_repair_cycle()
        except ValueError:
            pass

    def toggle_game_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.config(text="Resume")
            self.pause_all()
        else:
            self.pause_button.config(text="Pause")
            self.resume_all()

    def pause_all(self):
        for bird in self.birds:
            bird.is_flying = False

        for pillar in self.pillars:
            pillar.is_paused = True

        if self.spawn_timer:
            self.root.after_cancel(self.spawn_timer)
            self.spawn_timer = None
        if self.repair_timer:
            self.root.after_cancel(self.repair_timer)
            self.repair_timer = None

    def resume_all(self):
        for bird in self.birds:
            bird.is_flying = True
            if not bird.in_animation:  
                bird.fly_randomly()

        for pillar in self.pillars:
            pillar.is_paused = False
            pillar.monitor_load()  

        self.start_bird_spawning()
        self.start_pillar_repair_cycle()

    def on_canvas_click(self, event):
        x, y = event.x, event.y

        for pillar in self.pillars:
            if pillar.is_within_bounds(x, y):
                new_durability = self.durability_slider.get()
                pillar.max_load = new_durability
                print(f"Updated pillar at ({pillar.x_coord}, {pillar.y_coord}) to durability {pillar.max_load}")
                return

        for pillar in self.pillars:
            if abs(pillar.x_coord - x) < 100 and abs(pillar.y_coord - y) < 100:
                print("Too close to an existing pillar. Cannot place a new one.")
                return

        new_pillar = SupportPillar(self.canvas, self.durability_slider.get(), default_config['PILLAR_REPAIR_DELAY'], x, y, 20, 10)
        self.pillars.append(new_pillar)
        new_pillar.render()
        print(f"Added new pillar at ({x}, {y}) with durability {new_pillar.max_load}")


    def create_initial_pillars(self):
        self.pillars.clear()
        for i in range(4):
            pillar = SupportPillar(self.canvas, default_config['PILLAR_STRENGTH'], default_config['PILLAR_REPAIR_DELAY'], 70 * i + 50, 300, 20, 10)
            self.pillars.append(pillar)
            pillar.render()

    def spawn_initial_birds(self):
        self.birds.clear()
        for _ in range(default_config['BIRD_COUNT']):
            bird = FlyingBird(self.canvas, random.randint(1, 6), self.pillars)
            self.birds.append(bird)
            bird.render()
            bird.fly_randomly()

def main():
    root = Tk()
    root.resizable(True, True)
    app = BirdPillarGame(root)
    root.mainloop()

if __name__ == '__main__':  
    main()

