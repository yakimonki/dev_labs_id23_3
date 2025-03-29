from tkinter import *
import json
import random
from threading import Timer

try:
    with open("data.json", 'r') as a:
        b = json.load(a)
except FileNotFoundError:
    b = {
        'A': 5,
        'B': 2,
        'C': 5,
    }
    with open('data.json', 'w') as a:
        json.dump(b, a)


class d(Canvas):

    def __init__(self, e: Tk):
        super().__init__(e, width=500, height=500)
        self.pack()


class f:

    def __init__(self, g: d, h: int, i: int, j: int, k: int):
        self.m = h
        self.n = g
        self.o = i
        self.p = 0
        self.j = j
        self.q = False
        self.k = k
        self.r = None
        self.s = None
        self.t = True
        self.u()

    def v(self):
        self.r = self.n.create_rectangle(self.j, self.k, self.j + 10, self.k + 200, fill='brown', outline='brown')
        self.s = self.n.create_rectangle(self.j - 30, self.k, self.j + 40, self.k + 10, fill='brown', outline='brown')

    def w(self):
        self.p += 1

    def x(self):
        self.p -= 1

    def y(self):
        if not self.q:
            self.n.itemconfigure(self.s, state='hidden')
            self.n.itemconfigure(self.r, state='hidden')
            self.t = False
            self.q = True
            a = Timer(self.o, self.z)
            a.start()

    def z(self):
        self.n.itemconfigure(self.s, state='normal')
        self.n.itemconfigure(self.r, state='normal')
        self.t = True
        self.q = False

    def u(self):
        if self.t:
            if self.p >= self.m:
                self.y()

        self.n.after(100, self.u)


class aa:
    def __init__(self, g: d, bb: int, cc: [f]):
        self.dd = False
        self.ee = None
        self.bb = bb
        self.n = g
        self.ff = random.randint(50, 550)
        self.gg = random.randint(50, 250)
        self.hh = False
        self.ii = None
        self.jj = True
        self.cc = cc
        self.kk = None

    def ll(self):
        self.ii = self.n.create_oval(0, 0, 20, 20, fill='grey')
        self.n.coords(self.ii, self.ff - 10, self.gg - 10, self.ff + 10, self.gg + 10)

    def mm(self, nn, oo, pp=None):
        self.jj = False
        if not self.hh:
            self.hh = True
            pq = nn - self.ff
            rs = oo - self.gg
            self.ff = nn
            self.gg = oo
            st = (pq ** 2 + rs ** 2) ** .5
            uv = 10
            wx = uv / st * pq
            yz = uv / st * rs

            ab = 0

            def cd():
                nonlocal ab
                ab += uv
                if ab < st:
                    self.n.move(self.ii, wx, yz)
                    self.n.after(40, cd)
                else:
                    self.n.coords(self.ii, nn - 10, oo - 10, nn + 10, oo + 10)
                    self.hh = False
                    if self.kk is None and not self.dd:
                        self.jj = True
                        if self.ef():
                            self.gh()
                        else:
                            self.ij()
                    if pp is not None:
                        pp()

            cd()

    def ef(self):
        return any([bb.t for bb in self.cc])

    def ij(self):
        if not self.kk.t:
            if self.ee is not None:
                self.ee.cancel()
            self.jj = True
            self.kl()
            self.kk = None
        elif self.kk is not None:
            self.n.after(100, self.ij)

    def kl(self):
        self.ij()
        self.kk.w()

    def gh(self):
        self.jj = True
        self.mm(*random.choice([[i, -10] for i in range(-10, 500, 10)]))

    def gh(self):
        available = list(filter(lambda x: x.t, self.cc))
        self.kk = available[random.randint(0, len(available) - 1)]
        if self.kk.t:
            self.jj = False

            def on_done():
                self.kk.w()
                self.ee = Timer(self.bb, self.gh)
                self.ee.start()
                self.ij()

            self.mm(
                random.randrange(self.kk.j - 30, self.kk.j + 30, random.randint(1, 10)),
                self.kk.k, pp=on_done)
        else:
            self.kk = None
            self.gh()

def main():
    root = Tk()
    root.maxsize(500, 500)
    root.minsize(500, 500)
    n = d(root)
    cc = []
    for i in range(1, 5):
        bb = f(n, b['B'], b['C'], 70 * i + (50 * (i - 1)), 300)
        cc.append(bb)
        bb.v()

    aa_ = []
    for _ in range(b['A']):
        dd = aa(n, random.randint(1, 6), cc)
        aa_.append(dd)
        dd.ll()
        dd.gh()

    root.mainloop()


if __name__ == '__main__':
    main()
