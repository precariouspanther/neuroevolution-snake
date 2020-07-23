import pygame
import time
import random
from neuralnetwork import *
from snake import Grid, Population

population = Population(5, Vector(50, 50), 10, Vector(50, 50))

pygame.init()

white = (255, 255, 255)
yellow = (255, 255, 102)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)

display_width = 1100
display_height = 1000

dis = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('smart snake')

clock = pygame.time.Clock()

snake_block = 20
snake_speed = 15

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("bahnschrift", 15)


def show_score(score):
    value = score_font.render("Score: " + str(score), True, white)
    dis.blit(value, [0, 0])


def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [display_width / 6, display_height / 3])


def gameLoop():
    game_over = False
    game_close = False

    x1 = display_width / 2
    y1 = display_height / 2

    x1_change = 0
    y1_change = 0

    neural_network = NeuralNetwork(6, 2, 16, 5, ReLU())

    network_display = NetworkDisplay(neural_network, Vector(700, 40), Vector(300, 700), 10)

    while not game_over:
        # Ask the neural network to evaluate the snakes senses and make a move
        ml_input = neural_network.forward(population.snake_grids[0].snake.get_senses())[0]

        if ml_input[0] > 0.5:
            population.snake_grids[0].snake.up()
        if ml_input[1] > 0.5:
            population.snake_grids[0].snake.down()
        if ml_input[2] > 0.5:
            population.snake_grids[0].snake.left()
        if ml_input[3] > 0.5:
            population.snake_grids[0].snake.right()

        while game_close == True:
            dis.fill(blue)
            message("You Lost! Press C-Play Again or Q-Quit", red)
            show_score(population.snake_grids[0].snake.length * 10)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    population.snake_grids[0].snake.left()
                elif event.key == pygame.K_RIGHT:
                    population.snake_grids[0].snake.right()
                elif event.key == pygame.K_UP:
                    population.snake_grids[0].snake.up()
                elif event.key == pygame.K_DOWN:
                    population.snake_grids[0].snake.down()
                elif event.key == pygame.K_SPACE:
                    population.snake_grids[0].respawn()

        if x1 >= display_width or x1 < 0 or y1 >= display_height or y1 < 0:
            game_close = True
        x1 += x1_change
        y1 += y1_change
        dis.fill(black)

        show_score(population.snake_grids[0].snake.length * 10)

        population.draw(pygame, dis)
        network_display.draw(pygame, dis)

        pygame.display.update()
        clock.tick(snake_speed)

    pygame.quit()
    quit()


gameLoop()
