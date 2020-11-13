import os

import numpy as np
import neat
import re
import pygame as pg

from game import Game, Cell, GameAction, find_cell

pop_size = 50
game = Game(pop_size)

gen = 0


def calc_input(game, cell):
    inp = [cell.x, cell.y, cell.hp]

    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (0, 0)]:
        x = cell.x + dx
        y = cell.y + dy
        if 0 <= x < Cell.W and 0 <= y < Cell.H:
            inp.append(game.cells_food[y, x].count)
        else:
            inp.append(0)
    for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (-1, 1), (1, -1), (-1, -1), (1, 1)]:
        x = cell.x + dx
        y = cell.y + dy
        if (near_cell := find_cell(game, x, y)) is not None:
            inp.append(near_cell.hp > 0)
        else:
            inp.append(0)

    return inp


def eval_genomes(genomes, config):
    global game, gen
    win = game.screen

    gen += 1
    game.restart()

    nets = []
    cells = game.cells.copy()
    ge = []

    for num, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        ge.append(genome)

    iteration = 0
    every = 3
    while len(cells) > 0:
        game.draw()
        # score
        score_label = pg.font.SysFont("bahnschrift", 25).render("Alive: " + str(len(cells)), True, (255, 255, 255))
        win.blit(score_label, (Game.WIDTH - score_label.get_width() - 15, 10))
        if iteration % every == 0:
            game.tick()
        else:
            game.display_tick()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
                break

        rem = []
        for x, cell in enumerate(cells):
            inp = calc_input(game, cell)
            if cell.died:
                ge[x].fitness -= 1
                rem.append(cell)
                continue

            ge[x].fitness += 0.1 * cell.hp_delta
            outp = nets[x].activate((*inp, cell.hp, cell.x, cell.y))
            ind = np.argmax(outp)
            if ind == 0:
                dx, dy = 0, -1
            elif ind == 1:
                dx, dy = -1, 0
            elif ind == 2:
                dx, dy = 0, 1
            elif ind == 3:
                dx, dy = 1, 0
            else:
                raise RuntimeError('Unknown command from nn')
            if 0 <= cell.x + dx < Cell.W and 0 <= cell.y + dy < Cell.H:
                if not game.update(GameAction(cell.cell_id, dx, dy)):
                    ge[x].fitness -= 1
            else:
                ge[x].fitness -= 1

        for cell in rem:
            x = cells.index(cell)
            ge.pop(x)
            nets.pop(x)
            cells.pop(x)

        iteration += 1
        if iteration > 500:
            break


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 50)

    print(f'\nBest genome: {winner}')


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'neat.cfg')
    run(config_path)
