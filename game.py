from abc import ABC
from collections import namedtuple
from enum import IntEnum, auto

import numpy as np
import pygame as pg

pg.init()
font_style = pg.font.SysFont("bahnschrift", 13)


GameAction = namedtuple('GameAction', ['cell_id', 'dx', 'dy'])


def find_cell(game, xr, yr):
    for cell in game.cells:
        if cell.x == xr and cell.y == yr:
            return cell


class AbstractGameObject(ABC):
    def tick(self):
        raise NotImplementedError()


class Game(AbstractGameObject):
    WIDTH, HEIGHT = 1600, 900

    def __init__(self, pop_size):
        assert pop_size < Cell.H * Cell.W, "Population size too big"
        self.pop_size = pop_size
        self.RES = self.WIDTH, self.HEIGHT = Game.WIDTH, Game.HEIGHT
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 10
        self.screen = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()

        self.cells_food = np.array([[CellFood(x, y) for x in range(Cell.W)] for y in range(Cell.H)])

        self.cells = []
        self.generate()

    def draw(self):
        self.screen.fill(pg.Color('black'))
        self.draw_grid()
        self.draw_food()
        self.draw_cells()

    def draw_grid(self):
        for x in range(0, self.WIDTH, Cell.TILE):
            pg.draw.line(self.screen, pg.Color('dimgray'), (x, 0), (x, self.HEIGHT))
        for y in range(0, self.HEIGHT, Cell.TILE):
            pg.draw.line(self.screen, pg.Color('dimgray'), (0, y), (self.WIDTH, y))

    def _draw_tile(self, color, x, y):
        pg.draw.rect(self.screen, pg.Color(color),
                     (x * Cell.TILE + 2, y * Cell.TILE + 2, Cell.TILE - 2, Cell.TILE - 2))

    def draw_food(self):
        for y in range(Cell.H):
            for x in range(Cell.W):
                if self.cells_food[y, x].magic:
                    pass
                else:
                    self._draw_tile('forestgreen', x, y)
                render_hp = font_style.render(f'{self.cells_food[y][x].count}', True, pg.Color('yellow'))
                self.screen.blit(render_hp,
                                 (x * Cell.TILE + Cell.TILE // 2 - render_hp.get_width() // 2 + 2,
                                  y * Cell.TILE + Cell.TILE // 2 - render_hp.get_height() // 2 + 2))

    def draw_cells(self):
        for cell in self.cells:
            if not cell.died:
                self._draw_tile('red', cell.x, cell.y)
                render_hp = font_style.render(f'{cell.hp}', True, pg.Color('yellow'))
                self.screen.blit(render_hp,
                                 (cell.x * Cell.TILE + Cell.TILE // 2 - render_hp.get_width()//2 + 2,
                                  cell.y * Cell.TILE + Cell.TILE // 2 - render_hp.get_height()//2 + 2))

    def run(self):
        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    exit()
            self.tick()

    def generate(self):
        self.cells = [Cell(0, 0, cell_id) for cell_id in range(self.pop_size)]
        coords = [(x, y) for x in range(Cell.W) for y in range(Cell.H)]
        np.random.shuffle(coords)
        for i in range(self.pop_size):
            self.cells[i].x = coords[i][0]
            self.cells[i].y = coords[i][1]

        for y in range(Cell.H):
            for x in range(Cell.W):
                self.cells_food[y, x].count = np.random.randint(0, 100)
                self.cells_food[y, x].magic = False
        x = coords[self.pop_size][0]
        y = coords[self.pop_size][1]
        self.cells_food[y, x].magic = False

    def restart(self):
        self.cells.clear()
        self.generate()

    def update(self, game_action: GameAction):
        cell = self.cells[game_action.cell_id]
        for other_cell in self.cells:
            if cell.x + game_action.dx == other_cell.x and \
                    cell.y + game_action.dy == other_cell.y \
                    and other_cell.cell_id != cell.cell_id:
                return False
        cell.x += game_action.dx
        cell.y += game_action.dy
        cell.heal(self.cells_food[cell.y, cell.x].hit() // Cell.FOOD_DIV)
        return True

    def tick(self):
        for cell in self.cells:
            cell.tick()
        for cell in self.cells_food.reshape(-1):
            cell.tick()
        self.display_tick()

    def display_tick(self):
        pg.display.set_caption(f"{self.clock.get_fps()}")
        pg.display.flip()
        self.clock.tick(self.FPS)


class CellType(IntEnum):
    PEACEFUL = auto()


class Cell(AbstractGameObject):
    TILE = 50
    H = Game.HEIGHT // TILE
    W = Game.WIDTH // TILE

    HP_PER_TICK = -13

    FOOD_PER_TICK = 40
    FOOD_DIV = 2

    MAX_HP = 100
    MIN_HP = 0

    def __init__(self, x, y, cell_id=None):
        self.x, self.y = x, y

        self.hp = np.random.randint(Cell.MIN_HP + Cell.MAX_HP // 2, Cell.MAX_HP)
        self.type = CellType.PEACEFUL

        self.cell_id = cell_id

        self.hp_delta = 0

    def tick(self):
        delta = self.HP_PER_TICK
        # for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (-1, 1), (1, -1), (-1, -1), (1, 1)]:
        #     x = self.x + dx
        #     y = self.y + dy
        #     cell = find_cell(game, x, y)
        #     if cell is not None:
        #         delta = min(delta + 5, -2)
        #     if 0 <= x < Cell.W and 0 <= y < Cell.H and game.cells_food[y, x].magic:
        #         delta = 0
        #         break

        self.hp = max(self.hp + delta, Cell.MIN_HP)

    def heal(self, count=None):
        old_hp = self.hp
        if count is None:
            count = Cell.FOOD_PER_TICK // Cell.FOOD_DIV
        self.hp = self.hp + count
        self.hp_delta = self.hp - old_hp
        return self.hp_delta

    @property
    def died(self):
        return self.hp <= Cell.MIN_HP

    @property
    def alive(self):
        return not self.died


class CellFood(AbstractGameObject):
    MAX_COUNT = 40
    MIN_COUNT = 0
    TILE = Cell.TILE
    HP_DAMAGE = Cell.FOOD_PER_TICK
    FOOD_PER_TICK = 6

    def __init__(self, x, y, count=None, magic=False):
        self.x, self.y = x, y
        if count is None:
            count = np.random.randint(CellFood.MIN_COUNT, CellFood.MAX_COUNT)
        self.count = count
        self.min = np.random.randint(CellFood.MIN_COUNT, CellFood.MAX_COUNT // 3)
        self.max = np.random.randint(self.min, CellFood.MAX_COUNT)
        self.per_tick = np.random.randint(0, self.FOOD_PER_TICK)
        self.magic = magic

    def hit(self):
        old_count = self.count
        self.count = max(self.count - CellFood.HP_DAMAGE, self.min)
        count = old_count - self.count
        return count

    def tick(self):
        self.count = min(self.per_tick + self.count, self.max)


pop_size = 50
game = Game(pop_size)

if __name__ == '__main__':
    game.run()
