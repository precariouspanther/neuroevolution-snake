import matplotlib
import pygame
from matplotlib import pyplot as plt
import matplotlib.backends.backend_agg as agg


class Graph(object):
    def __init__(self):
        matplotlib.style.use("seaborn")
        matplotlib.use("Agg")
        matplotlib.rcParams.update({'font.size': 11})
        self.fig = plt.figure(figsize=[4, 2])

        self.ax = self.fig.add_subplot(111)
        self.ax.set_yscale("log")

        self.canvas = agg.FigureCanvasAgg(self.fig)
        self.fig.tight_layout()

    def draw(self, data, xlabel: str, ylabel: str, yscale: str = "log"):
        self.ax.clear()

        self.ax.set_xlabel(xlabel, color='k', labelpad=10)
        self.ax.set_ylabel(ylabel, rotation=270, color='k', labelpad=15)
        self.ax.set_yscale(yscale)

        self.ax.plot(data)
        self.fig.tight_layout()
        self.canvas.draw()
        raw_data = self.canvas.get_renderer().tostring_rgb()
        size = self.canvas.get_width_height()

        return pygame.image.fromstring(raw_data, size, "RGB")
