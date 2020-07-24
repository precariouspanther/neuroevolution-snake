from neuralnetwork import *
from population import Population
from save import SaveState

pygame.init()

display_width = 1100
display_height = 1000

display = pygame.display.set_mode((display_width, display_height))

pygame.display.set_caption('smart snake')
clock = pygame.time.Clock()

font = pygame.font.SysFont('bahnschrift', 15)


def gameLoop():
    exit_game = False

    population = Population(1000, Vector(50, 50), 10, Vector(50, 50))

    save_state = SaveState('saved-population.dat')

    # Display the first snakes brain in the HUD
    network_display = NetworkDisplay(population.active_snake.brain, Vector(700, 80), Vector(300, 800), 10)

    while not exit_game:
        network_display.network = population.active_snake.brain

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    population.snakes[0].left()
                elif event.key == pygame.K_RIGHT:
                    population.snakes[0].right()
                elif event.key == pygame.K_UP:
                    population.snakes[0].up()
                elif event.key == pygame.K_DOWN:
                    population.snakes[0].down()
                elif event.key == pygame.K_F1:
                    save_state.save(population)
                elif event.key == pygame.K_F2:
                    del population
                    population = save_state.open()
                    network_display.network = population.active_snake.brain

        display.fill((0, 0, 0))

        value = font.render("Live snakes: " + str(population.live_snakes()) + "/" + str(len(population.snakes)),
                            True, (255, 255, 255))
        display.blit(value, [200, 0])

        value = font.render("Best score: " + str(population.best_score), True, (255, 255, 255))
        display.blit(value, [400, 0])

        value = font.render("Generation: " + str(population.generations), True, (255, 255, 255))
        display.blit(value, [600, 0])

        value = font.render("Max Length: " + str(population.best_length), True, (255, 255, 255))
        display.blit(value, [800, 0])

        population.draw(pygame, display)
        network_display.draw(pygame, display)

        pygame.display.update()
        clock.tick(25)

    pygame.quit()
    quit()


gameLoop()
