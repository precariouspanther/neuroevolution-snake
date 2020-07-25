from matplotlib import pyplot as plt


class Graph(object):
    def draw(self, data):
        generations = []
        scores = []
        for i, score in enumerate(data):
            generations.append(i)
            scores.append(score)

        plt.plot(generations, scores)
        plt.show()
