from tkinter import *
import json as j
import random as r
from threading import Timer as T

try:
    with open("data.json", 'r') as s:
        _ = j.load(s)
except FileNotFoundError:
    _ = {'A': 5, 'B': 2, 'C': 5}
    with open('data.json', 'w') as s:
        j.dump(_, s)


class X(Canvas):
    def __init__(self, y: Tk):
        super().__init__(y, width=500, height=500)
        self.pack()


class Q:
    def __init__(self, g: X, l: int, w: int, x: int, y: int):
        self.l = l
        self.g = g
        self.w = w
        self.k = 0
        self.x = x
        self.b = False
        self.y = y
        self.s, self.r = None, None
        self.a = True
        self.v()

    def f(self):
        self.s = self.g.create_rectangle(self.x, self.y, self.x + 10, self.y + 200, fill='brown', outline='brown')
        self.r = self.g.create_rectangle(self.x - 30, self.y, self.x + 40, self.y + 10, fill='brown', outline='brown')

    def i(self):
        self.k += 1

    def d(self):
        self.k -= 1

    def bq(self):
        if not self.b:
            self.g.itemconfigure(self.r, state='hidden')
            self.g.itemconfigure(self.s, state='hidden')
            self.a = False
            self.b = True
            t = T(self.w, self.fq)
            t.start()

    def fq(self):
        self.g.itemconfigure(self.r, state='normal')
        self.g.itemconfigure(self.s, state='normal')
        self.a = True
        self.b = False

    def v(self):
        if self.a:
            if self.k >= self.l:
                self.bq()
        self.g.after(100, self.v)


class Y:
    def __init__(self, g: X, z: int, q: [Q]):
        self.leave = False
        self.lt = None
        self.z = z
        self.g = g
        self.x = r.randint(50, 550)
        self.y = r.randint(50, 250)
        self.ap = False
        self.id = None
        self.flyable = True
        self.q = q
        self.cp = None

    def dr(self):
        self.id = self.g.create_oval(0, 0, 20, 20, fill='grey')
        self.g.coords(self.id, self.x - 10, self.y - 10, self.x + 10, self.y + 10)

    def anim(self, a, b, on_end=None):
        self.flyable = False
        if not self.ap:
            self.ap = True
            dx, dy = a - self.x, b - self.y
            self.x, self.y = a, b
            l = (dx ** 2 + dy ** 2) ** .5
            s, sx, sy = 10, s / l * dx, s / l * dy
            p = 0

            def animate():
                nonlocal p
                p += s
                if p < l:
                    self.g.move(self.id, sx, sy)
                    self.g.after(40, animate)
                else:
                    self.g.coords(self.id, a - 10, b - 10, a + 10, b + 10)
                    self.ap = False
                    if self.cp is None and not self.leave:
                        self.flyable = True
                        if self.cst():
                            self.crp()
                        else:
                            self.fly()
                    if on_end is not None:
                        on_end()

            animate()

    def cst(self):
        return any([p.a for p in self.q])

    def check_pillar(self):
        if not self.cp.a:
            if self.lt is not None:
                self.lt.cancel()
            self.flyable = True
            self.fa()
            self.cp = None
        elif self.cp is not None:
            self.g.after(100, self.check_pillar)

    def fa(self):
        self.fly()
        self.cp.d()

    def leave_func(self):
        self.leave = True
        self.flyable = True
        self.anim(*r.choice([[i, -10] for i in range(-10, 500, 10)]))

    def crp(self):
        ap = list(filter(lambda x: x.a, self.q))
        self.cp = ap[r.randint(0, len(ap) - 1)]
        if self.cp.a:
            self.flyable = False

            def end_func():
                self.cp.i()
                self.lt = T(self.z, self.leave_func)
                self.lt.start()
                self.check_pillar()

            self.anim(r.randrange(self.cp.x - 30, self.cp.x + 30, r.randint(1, 10)), self.cp.y, on_end=end_func)
        else:
            self.cp = None
            self.fly()

    def fly(self):
        if self.flyable and not self.leave:
            a, b = r.randint(10, 490), r.randint(10, 240)

            def end_func():
                self.g.after(50, self.fly)

            self.anim(a, b, on_end=end_func)


def main():
    root = Tk()
    root.maxsize(500, 500)
    root.minsize(500, 500)
    g = X(root)
    qs = []
    for i in range(1, 5):
        q = Q(g, _['B'], _['C'], 70 * i + (50 * (i - 1)), 300)
        qs.append(q)
        q.f()

    birds = []
    for _ in range(_['A']):
        bird = Y(g, r.randint(1, 6), qs)
        birds.append(bird)
        bird.dr()
        bird.fly()

    root.mainloop()


if __name__ == '__main__':
    main()
