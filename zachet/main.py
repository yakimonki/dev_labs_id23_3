# 13 вариант


import tkinter as tk


class ElevatorSimulator:
    def __init__(self, root):
        self.root = root

        self.floors_label = tk.Label(root, text="количество этажей:")
        self.floors_label.grid(row=0, column=0)

        self.floors_spinbox = tk.Spinbox(root, from_=2, to=20, width=5)
        self.floors_spinbox.grid(row=0, column=1)

        self.motor_power_label = tk.Label(root, text='мощность мотора')
        self.motor_power_label.grid(row=1, column=0)

        self.motor_power_slider = tk.Scale(root, from_=1, to=10, orient=tk.HORIZONTAL)
        self.motor_power_slider.grid(row=1, column=1)

        self.cargo_weight_label = tk.Label(root, text='вес груза')
        self.cargo_weight_label.grid(row=2, column=0)

        self.cargo_weight_spinbox = tk.Spinbox(root, from_=1, to=1000, width=5)
        self.cargo_weight_spinbox.grid(row=2, column=1)

        self.start_button = tk.Button(root, text='старт', command=self.start_animation)
        self.start_button.grid(row=3, column=0, columnspan=2)

        self.reset_button = tk.Button(root, text='сброс', command=self.reset_position)
        self.reset_button.grid(row=4, column=0, columnspan=2)

        self.canvas = tk.Canvas(root, width=300, height=300)
        self.canvas.grid(row=5, column=0, columnspan=2)

        self.elevator_position = 1
        self.elevator = self.canvas.create_rectangle(130, 250, 170, 270, fill="blue")
        self.animating = False

    def start_animation(self):
        if self.animating:
            return
        self.animating = True

        self.floors = int(self.floors_spinbox.get())
        self.motor_power = self.motor_power_slider.get()
        self.cargo_weight = int(self.cargo_weight_spinbox.get())

        self.speed = self.motor_power / self.cargo_weight

        self.move_up(1)

    def move_up(self, floor):
        if floor > self.floors:
            self.move_down(self.floors)
            return

        y_position = 250 - (floor * 20)
        self.canvas.coords(self.elevator, 130, y_position, 170, y_position + 20)

        self.root.after(int(self.speed * 1000), self.move_up, floor + 1)

    def move_down(self, floor):
        if floor == 0:
            self.animating = False
            return

        y_position = 250 - (floor * 20)
        self.canvas.coords(self.elevator, 130, y_position, 170, y_position + 20)

        self.root.after(int(self.speed * 1000), self.move_down, floor - 1)

    def reset_position(self):
        self.canvas.coords(self.elevator, 130, 250, 170, 270)
        self.animating = False


if __name__ == "__main__":
    root = tk.Tk()
    simulator = ElevatorSimulator(root)
    root.mainloop()
