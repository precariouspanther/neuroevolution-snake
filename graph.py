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
        #self.fig.set_facecolor((0, 0, 0))
        #self.ax.set_facecolor((0.31, 0.31, 0.31))

        self.canvas = agg.FigureCanvasAgg(self.fig)
        self.fig.tight_layout()

    def draw(self, data):
        generations = []
        scores = []
        for i, score in enumerate(data):
            generations.append(i)
            scores.append(score)

        self.ax.clear()

        self.ax.set_xlabel("Generation", color='k', labelpad=10)
        self.ax.set_ylabel("Fitness", rotation=270, color='k', labelpad=15)
        self.ax.set_yscale("log")

        self.ax.plot(data)
        self.fig.tight_layout()
        self.canvas.draw()
        raw_data = self.canvas.get_renderer().tostring_rgb()
        size = self.canvas.get_width_height()

        return pygame.image.fromstring(raw_data, size, "RGB")
