import random
import json
from tkinter import *
from threading import Timer


class MainCanvas(Canvas):

    def __init__(self, root: Tk):
        super().__init__(root, width=500, height=500)
        self.is_paused = False
        self.pack()


class Pillars:

    def __init__(self, canvas: MainCanvas, max_birds: int, revival_time: int, x: int, y: int):
        self.max_birds = max_birds
        self.canvas = canvas
        self.revival_time = revival_time
        self.quantity_birds = 0
        self.x = x
        self.fall_pillar_flag = False
        self.y = y
        self.pole_id = None
        self.beam_id = None
        self.is_fixed = True
        self.register_birds()

    def draw_pillar(self):
        self.pole_id = self.canvas.create_rectangle(self.x, self.y, self.x + 10, self.y + 200, fill='gray',
                                                    outline='gray')
        self.beam_id = self.canvas.create_rectangle(self.x - 30, self.y, self.x + 40, self.y + 10, fill='gray',
                                                    outline='gray')

    def add_birds_count(self):
        self.quantity_birds += 1

    def delete_birds_count(self):
        self.quantity_birds -= 1

    def fall_pillar(self):
        if not self.fall_pillar_flag:
            self.canvas.itemconfigure(self.beam_id, state='hidden')
            self.canvas.itemconfigure(self.pole_id, state='hidden')
            self.is_fixed = False
            self.fall_pillar_flag = True
            timer = Timer(self.revival_time, self.set_pillar)
            timer.start()

    def set_pillar(self):
        self.canvas.itemconfigure(self.beam_id, state='normal')
        self.canvas.itemconfigure(self.pole_id, state='normal')
        self.is_fixed = True
        self.fall_pillar_flag = False

    def register_birds(self):
        if self.is_fixed:
            if self.quantity_birds >= self.max_birds:
                self.fall_pillar()

        self.canvas.after(100, self.register_birds)


class Birds:

    def __init__(self, canvas: MainCanvas, sitting_time: int, pillars: [Pillars]):
        self.is_flown = False
        self.left_time = None
        self.sit_timer = sitting_time
        self.canvas = canvas
        self.x = random.randint(50, 550)
        self.y = random.randint(50, 250)
        self.animation_progress = False
        self.id_bird = None
        self.is_able_to_fly = True
        self.current_pillar = None
        self.pillars = pillars

    def draw_bird(self):
        self.id_bird = self.canvas.create_oval(0, 0, 20, 20, fill='red')
        self.canvas.coords(self.id_bird, self.x - 10, self.y - 10, self.x + 10, self.y + 10)

    def animate(self, x, y, on_animation_ended=None):
        self.is_able_to_fly = False
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

            def animation():
                nonlocal progress
                progress += step
                if progress < length:
                    self.canvas.move(self.id_bird, step_x, step_y)
                    self.canvas.after(40, animation)
                else:
                    self.canvas.coords(self.id_bird, x - 10, y - 10, x + 10, y + 10)
                    self.animation_progress = False
                    if self.current_pillar is None and not self.is_flown:
                        self.is_can_fly = True
                        if self.able_to_seat():
                            self.choose_pillar()
                        else:
                            self.flying()
                    if on_animation_ended is not None:
                        on_animation_ended()

            animation()

    def able_to_seat(self):
        return any([pillar.is_fixed for pillar in self.pillars])

    def is_pillar_falled(self):
        if not self.current_pillar.is_fixed:
            if self.left_time is not None:
                self.left_time.cancel()
            self.is_able_to_fly = True
            self.fly_away()
            self.current_pillar = None
        elif self.current_pillar is not None:
            self.canvas.after(100, self.is_pillar_falled)

    def fly_away(self):
        self.flying()
        self.current_pillar.delete_birds_count()

    def leaving(self):
        self.is_flown = True
        self.is_able_to_fly = True

        self.animate(*random.choice([[i, -10] for i in range(-10, 500, 10)]))

    def choose_pillar(self):
        available_pillars = list(filter(lambda x: x.is_fixed, self.pillars))
        self.current_pillar = available_pillars[random.randint(0, len(available_pillars) - 1)]
        if self.current_pillar.is_fixed:
            self.is_able_to_fly = False

            def on_animation():
                self.current_pillar.add_birds_count()
                self.leave_timer = Timer(self.sit_timer, self.leaving)
                self.leave_timer.start()
                self.is_pillar_falled()

            self.animate(
                random.randrange(self.current_pillar.x - 30, self.current_pillar.x + 30, random.randint(1, 10)),
                self.current_pillar.y, on_animation_ended=on_animation)
        else:
            self.current_pillar = None
            self.flying()

    def flying(self):
        if self.is_able_to_fly and not self.is_flown:
            x = random.randint(10, 490)
            y = random.randint(10, 240)

            def on_animation():
                self.canvas.after(50, self.flying)

            self.animate(x, y, on_animation_ended=on_animation)


try:
    with open("data_birds.json", 'r') as settings:
        base_settings = json.load(settings)
except FileNotFoundError:
    base_settings = {
        'BIRDS_COUNT': 5,
        'PILLARS_DURABILITY': 2,
        'PILLARS_REPAIR_INTERVAL': 5,
    }
    with open('data_birds.json', 'w') as settings:
        json.dump(base_settings, settings)


def update_birds(slider_value, birds_list, canvas, pillars_list):
    diff = int(slider_value) - len(birds_list)
    if diff > 0:
        for _ in range(diff):
            bird = Birds(canvas, random.randint(1, 6), pillars_list)
            birds_list.append(bird)
            bird.draw_bird()
            bird.flying()
    elif diff < 0:
        for _ in range(-diff):
            bird = birds_list.pop()
            canvas.delete(bird.id_bird)


def update_pillars(slider_value, pillars_list, canvas):
    for pillar in pillars_list:
        pillar.max_birds = int(slider_value)


def toggle_pause(canvas: MainCanvas):
    canvas.is_paused = not canvas.is_paused


def add_pillar(event, pillars_list, canvas):
    x, y = event.x, event.y
    pillar = Pillars(canvas, base_settings['PILLARS_DURABILITY'], base_settings['PILLARS_REPAIR_INTERVAL'], x, y)
    pillars_list.append(pillar)
    pillar.draw_pillar()


def main():
    root = Tk()
    root.overrideredirect(1)
    root.state('zoomed')
    canvas = MainCanvas(root)

    control_frame = Frame(root)
    control_frame.pack(fill=X)

    pillars_list = []
    for i in range(1, 5):
        pillar = Pillars(canvas, base_settings['PILLARS_DURABILITY'], base_settings['PILLARS_REPAIR_INTERVAL'],
                         70 * i + (50 * (i - 1)), 300)
        pillars_list.append(pillar)
        pillar.draw_pillar()

    birds_list = []
    for _ in range(base_settings['BIRDS_COUNT']):
        bird = Birds(canvas, random.randint(1, 6), pillars_list)
        birds_list.append(bird)
        bird.draw_bird()
        bird.flying()

    pillars_slider = Scale(control_frame, from_=1, to=10, orient=HORIZONTAL, label="Прочность столбов")
    pillars_slider.set(base_settings['PILLARS_DURABILITY'])
    pillars_slider.pack(fill=X, padx=10, pady=5)
    pillars_slider.bind("<Motion>", lambda _: update_pillars(pillars_slider.get(), pillars_list, canvas))

    birds_slider = Scale(control_frame, from_=1, to=20, orient=HORIZONTAL, label="Время пояиления птиц")
    birds_slider.set(base_settings["BIRDS_SPAWN_INTERVAL"])
    birds_slider.pack(fill=X, padx=10, pady=5)
    birds_slider.bind("<Motion>", lambda _: update_birds(birds_slider.get(), birds_list, canvas, pillars_list))

    canvas.bind("<Button-1>", lambda event: add_pillar(event, pillars_list, canvas))

    pause_button = Button(control_frame, text="Пауза", command=lambda: toggle_pause(canvas))
    pause_button.pack(side=RIGHT, padx=5, pady=5)

    root.mainloop()


if __name__ == '__main__':
    main()
