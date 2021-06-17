import pygame
import math
from queue import PriorityQueue
from collections import deque
from tkinter import messagebox, Tk

WIDTH = 800
WIN = pygame.display.set_mode((1200, 800))
pygame.init()
pygame.display.set_caption("Path Finding Visualiser")

lightblue = (64, 206, 227)
purple = (197, 114, 255)
white = (255, 255, 255)
black = (50, 50, 50)
yellow = (255, 254, 106)
green = (126, 217, 87)
gridcolor = (175, 216, 248)
orange = (255, 165, 0)
font = pygame.font.Font("elements/myfont.ttf", 40)
algos=['  A-Star','Dijkstras','   Greedy']
menu = pygame.image.load('elements/Visualizer-UI.png')

# ------------------------------------------class for nodes in grid --------------------------------------------------------
class Box:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = white
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def getPos(self):
        return self.row, self.col

    def isStart(self):
        return self.color == green

    def isEnd(self):
        return self.color == orange       

    def isBarrier(self):
        return self.color == black

    def reset(self):
        self.color = white

    def makeStart(self):
        self.color = green

    def makeClosed(self):
        self.color = lightblue

    def makeOpen(self):
        self.color = purple

    def makeBarrier(self):
        self.color = black

    def makeEnd(self):
        self.color = orange

    def makePath(self):
        self.color = yellow


    def draw(self, win):
        pygame.draw.rect(
            win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # DOWN
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].isBarrier():
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        # RIGHT
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].isBarrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].isBarrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def heu_func(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.makePath()
        draw()

# ---------------------------------------------------------ALGORITHMS--------------------------------------------------------

def astar(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {box: float("inf") for row in grid for box in row}
    g_score[start] = 0
    final_score = {box: float("inf") for row in grid for box in row}
    final_score[start] = heu_func(start.getPos(), end.getPos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.makeEnd()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                final_score[neighbor] = temp_g_score + \
                    heu_func(neighbor.getPos(), end.getPos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((final_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.makeOpen()

        draw()

        if current != start:
            current.makeClosed()

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
            end.makeEnd()
            return True

        for neighbor in current.neighbors:
            if neighbor not in visited:
                visited.append(neighbor)
                came_from[neighbor] = current
                queue.append(neighbor)
                neighbor.makeOpen()
        draw()
        if current != start:
            current.makeClosed()

    return False


def greedy(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    final_score = {box: float("inf") for row in grid for box in row}
    final_score[start] = heu_func(start.getPos(), end.getPos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.makeEnd()
            return True

        for neighbor in current.neighbors:
            temp_f_score = heu_func(neighbor.getPos(), end.getPos())

            if temp_f_score < final_score[neighbor]:
                came_from[neighbor] = current
                final_score[neighbor] = temp_f_score
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((final_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.makeOpen()

        draw()

        if current != start:
            current.makeClosed()

    return False

# -------------------------------------------------------------GRID FUNCTIONS------------------------------------------

def clear(grid):
    for row in grid:
        for box in row:
            if not (box.isStart() or box.isEnd() or box.isBarrier()):
                box.reset()

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            box = Box(i, j, gap, rows)
            grid[i].append(box)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, gridcolor, (1, i * gap), (width, i * gap))
        for j in range(rows+1):
            pygame.draw.line(win, gridcolor, (j * gap, 0), (j * gap, width))


#------------------------------------------USED FOR DRAWING MENU AND GRID IN PYGAME ------------------------------------

def draw(win, grid, rows, width,selector):
    win.fill(white)
    win.blit(menu, (800, 0))
    for row in grid:
        for box in row:
            box.draw(win)

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
                                for box in row:
                                    box.update_neighbors(grid)
                            flag=astar(lambda: draw(win, grid, ROWS, width,selector),
                                grid, start, end)
                            start.makeStart()
                            if not flag:
                                Tk().wm_withdraw()
                                messagebox.showinfo("No Solution", "There was no solution")
                            
                        if selector == 1:
                            for row in grid:
                                for box in row:
                                    box.update_neighbors(grid)

                            flag=dj_algorithm(lambda: draw(win, grid, ROWS, width,selector),
                                 grid, start, end)
                            start.makeStart()

                            if not flag:
                                Tk().wm_withdraw()
                                messagebox.showinfo("No Solution", "There was no solution")
                        
                        if selector == 2:
                            for row in grid:
                                for box in row:
                                    box.update_neighbors(grid)

                            flag=greedy(lambda: draw(win, grid, ROWS, width,selector),
                                 grid, start, end)
                            start.makeStart()

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
                    box = grid[row][col]
                    if not start and box != end:
                        start = box
                        start.makeStart()

                    elif not end and box != start:
                        end = box
                        end.makeEnd()

                    elif box != end and box != start:
                        box.makeBarrier()

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                pos = pygame.mouse.get_pos()
                if(800 < pos[0] < 1200):
                    #print("MENU")
                    pass
                else:
                    row, col = get_clicked_pos(pos, ROWS, width)
                    box = grid[row][col]
                    box.reset()
                    if box == start:
                        start = None
                    elif box == end:
                        end = None


    pygame.quit()


main(WIN, WIDTH)
