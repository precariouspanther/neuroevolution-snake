import matplotlib
import pygame
from matplotlib import pyplot as plt
import matplotlib.backends.backend_agg as agg


class Graph(object):
    def __init__(self):
        matplotlib.use("Agg")
        fig = plt.figure(figsize=[4, 2])
        self.ax = fig.add_subplot(111)
        self.canvas = agg.FigureCanvasAgg(fig)

    def draw(self, data):
        generations = []
        scores = []
        for i, score in enumerate(data):
            generations.append(i)
            scores.append(score)

        self.ax.clear()
        self.ax.plot(data)
        self.canvas.draw()
        renderer = self.canvas.get_renderer()

        raw_data = renderer.tostring_rgb()
        size = self.canvas.get_width_height()

        return pygame.image.fromstring(raw_data, size, "RGB")
