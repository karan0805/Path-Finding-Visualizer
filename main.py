import pygame
import math
from queue import PriorityQueue
from collections import deque
from tkinter import messagebox, Tk

WIDTH = 800
WIN = pygame.display.set_mode((1200, 800))
pygame.init()
pygame.display.set_caption("Path Finding Visualiser")

LIGHTBLUE = (64, 206, 227)
PURPLE = (197, 114, 255)
#YELLOW2 = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (50, 50, 50)
YELLOW = (255, 254, 106)
GREEN = (126, 217, 87)
GRIDCOLOUR = (175, 216, 248)
ORANGE = (255, 165, 0)
font = pygame.font.Font("elements/myfont.ttf", 40)
algos=['  A-Star','Dijkstras','   Greedy']
menu = pygame.image.load('elements/Visualizer-UI.png')

# ------------------------------------------class for nodes in grid --------------------------------------------------------
class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == LIGHTBLUE

    def is_open(self):
        return self.color == PURPLE

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == GREEN

    def is_end(self):
        return self.color == ORANGE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = GREEN

    def make_closed(self):
        self.color = LIGHTBLUE

    def make_open(self):
        self.color = PURPLE

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = ORANGE

    def make_path(self):
        self.color = YELLOW

    # def make_current(self):
    #     self.color = YELLOW2

    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

# ---------------------------------------------------------ALGORITHMS--------------------------------------------------------

def astar(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + \
                    h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def dj_algorithm(draw, grid, start, end):
    came_from = {}
    queue, visited = deque(), []

    queue.append(start)
    visited.append(start)

    while len(queue) > 0:
        current = queue.popleft()
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited:
                visited.append(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
                neighbor.make_open()
        draw()
        if current != start:
            current.make_closed()

    return False


def greedy(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_f_score = h(neighbor.get_pos(), end.get_pos())

            if temp_f_score < f_score[neighbor]:
                came_from[neighbor] = current
                f_score[neighbor] = temp_f_score
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False

# -------------------------------------------------------------GRID FUNCTIONS------------------------------------------

def clear(grid):
    for row in grid:
        for spot in row:
            if not (spot.is_start() or spot.is_end() or spot.is_barrier()):
                spot.reset()

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GRIDCOLOUR, (1, i * gap), (width, i * gap))
        for j in range(rows+1):
            pygame.draw.line(win, GRIDCOLOUR, (j * gap, 0), (j * gap, width))


#------------------------------------------USED FOR DRAWING MENU AND GRID IN PYGAME ------------------------------------

def draw(win, grid, rows, width,selector):
    win.fill(WHITE)
    win.blit(menu, (800, 0))
    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    algoname = font.render(algos[selector], True, (255, 255, 255))
    win.blit(algoname, (910, 430))
    pygame.display.update()


def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col


def main(win, width):
    ROWS = 25
    grid = make_grid(ROWS, width)

    start = None
    end = None
    selector = 0
    run = True
    while run:
        draw(win, grid, ROWS, width,selector)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # LEFT
                pos = pygame.mouse.get_pos()
                #print(pos)
                if (800 <= pos[0] <= 1200):
                    if(895 <= pos[0] <= 1105 and 535 <= pos[1] <= 610 and start and end):
                        clear(grid)
                        if selector == 0:
                            for row in grid:
                                for spot in row:
                                    spot.update_neighbors(grid)
                            flag=astar(lambda: draw(win, grid, ROWS, width,selector),
                                grid, start, end)
                            start.make_start()
                            if not flag:
                                Tk().wm_withdraw()
                                messagebox.showinfo("No Solution", "There was no solution")
                            
                        if selector == 1:
                            for row in grid:
                                for spot in row:
                                    spot.update_neighbors(grid)

                            flag=dj_algorithm(lambda: draw(win, grid, ROWS, width,selector),
                                 grid, start, end)
                            start.make_start()

                            if not flag:
                                Tk().wm_withdraw()
                                messagebox.showinfo("No Solution", "There was no solution")
                        
                        if selector == 2:
                            for row in grid:
                                for spot in row:
                                    spot.update_neighbors(grid)

                            flag=greedy(lambda: draw(win, grid, ROWS, width,selector),
                                 grid, start, end)
                            start.make_start()

                            if not flag:
                                Tk().wm_withdraw()
                                messagebox.showinfo("No Solution", "There was no solution")

                    if(895 <= pos[0] <= 1105 and 620 <= pos[1] <= 695):
                        clear(grid)                    
                        
                    if(895 <= pos[0] <= 1105 and 710 <= pos[1] <= 785):
                        start = None
                        end = None
                        grid = make_grid(ROWS, width)



                    if (801<= pos[0] <= 878 and 426 <= pos[1] <=501):
                        #print('left')
                        if selector == 0:
                            selector = 3
                        selector -= 1
                        #selector = (selector-1)%3

                    if (1123<= pos[0] <= 1200 and 426 <= pos[1] <= 501):
                        #print('right')
                        selector = (abs(selector+1))%3
                        #76 x 76

                else:
                    row, col = get_clicked_pos(pos, ROWS, width)
                    spot = grid[row][col]
                    if not start and spot != end:
                        start = spot
                        start.make_start()

                    elif not end and spot != start:
                        end = spot
                        end.make_end()

                    elif spot != end and spot != start:
                        spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                pos = pygame.mouse.get_pos()
                if(800 < pos[0] < 1200):
                    #print("MENU")
                    pass
                else:
                    row, col = get_clicked_pos(pos, ROWS, width)
                    spot = grid[row][col]
                    spot.reset()
                    if spot == start:
                        start = None
                    elif spot == end:
                        end = None

            # ---------------------------------------- Keyboard Bindings ------------------------------------------------------------------
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE and start and end:
            #         for row in grid:
            #             for spot in row:
            #                 spot.update_neighbors(grid)

            #         astar(lambda: draw(win, grid, ROWS, width,selector),
            #                   grid, start, end)
            #         start.make_start()
            #     if event.key == pygame.K_c:
            #         start = None
            #         end = None
            #         grid = make_grid(ROWS, width)


    pygame.quit()


main(WIN, WIDTH)
