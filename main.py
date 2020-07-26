from graph import Graph
from neuralnetwork import *
from population import Population
from save import SaveState


class Game(object):
    def __init__(self):
        pygame.init()

        self.display = pygame.display.set_mode((1700, 1000))

        pygame.display.set_caption('smart snake')
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont('bahnschrift', 15)
        self.graph_writer = Graph()
        self.fitness_graph = None
        self.length_graph = None
        self.duration_graph = None
        self.population = Population(1000, Vector(50, 50), 10, Vector(50, 50))
        self.pause = False

    def refresh_graphs(self):
        self.fitness_graph = self.graph_writer.draw([x['score'] for x in self.population.history], "Generation",
                                                    "Fitness", "linear")
        self.length_graph = self.graph_writer.draw([x['length'] for x in self.population.history], "Generation",
                                                   "Length", "linear")
        self.duration_graph = self.graph_writer.draw([x['duration'] for x in self.population.history], "Generation",
                                                     "Seconds", "linear")

    def gameLoop(self):
        exit_game = False

        save_state = SaveState('saved-population.dat')

        # Display the first snakes brain in the HUD
        network_display = NetworkDisplay(self.population.active_snake.brain, Vector(700, 80), Vector(300, 800), 10)
        # Display generation history
        self.refresh_graphs()

        self.population.on_generation = self.refresh_graphs

        while not exit_game:
            network_display.network = self.population.active_snake.brain

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.population.snakes[0].left()
                    elif event.key == pygame.K_RIGHT:
                        self.population.snakes[0].right()
                    elif event.key == pygame.K_UP:
                        self.population.snakes[0].up()
                    elif event.key == pygame.K_DOWN:
                        self.population.snakes[0].down()
                    elif event.key == pygame.K_F1:
                        save_state.save(self.population.save_data())
                    elif event.key == pygame.K_SPACE:
                        if self.pause:
                            self.pause = False
                        else:
                            self.pause = True
                    elif event.key == pygame.K_F2:
                        self.population.load_data(save_state.open())
                        network_display.network = self.population.active_snake.brain

            self.display.fill((0, 0, 0))

            value = self.font.render(
                "Live snakes: " + str(self.population.live_snakes()) + "/" + str(len(self.population.snakes)),
                True, (255, 255, 255))
            self.display.blit(value, [200, 0])

            value = self.font.render("Best score: " + str(self.population.best_score), True, (255, 255, 255))
            self.display.blit(value, [400, 0])

            value = self.font.render("Generation: " + str(self.population.generations), True, (255, 255, 255))
            self.display.blit(value, [800, 0])

            value = self.font.render(
                "Length: " + str(self.population.active_snake.length) + " / " + str(self.population.best_length), True,
                (255, 255, 255))
            self.display.blit(value, [950, 0])

            if not self.pause:
                self.population.move()
            self.population.draw(pygame, self.display)
            network_display.draw(pygame, self.display)

            self.display.blit(self.fitness_graph, (1200, 50))
            self.display.blit(self.length_graph, (1200, 251))
            self.display.blit(self.duration_graph, (1200, 452))

            pygame.display.update()
            self.clock.tick(100)

        pygame.quit()
        quit()


game = Game()
game.gameLoop()
