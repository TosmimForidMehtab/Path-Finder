import pygame
import math
from queue import PriorityQueue

WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Path Finder")

RED = (204, 0, 0)
GREEN = (0, 102, 0)
BLUE = (0, 0, 204)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 128, 255)
PINK = (255, 0, 255)
GREY = (128, 128, 128)
# BLUE = (64, 224, 208)


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

    def getPos(self):
        return self.row, self.col

    def isClosed(self):
        return self.color == BLUE

    def isOpen(self):
        return self.color == PINK

    def isBarrier(self):
        return self.color == BLACK

    def isStart(self):
        return self.color == RED

    def isEnd(self):
        return self.color == GREEN

    def reset(self):
        self.color = WHITE

    def makeStart(self):
        self.color = RED

    def makeClosed(self):
        self.color = BLUE

    def makeOpen(self):
        self.color = PINK

    def makeBarrier(self):
        self.color = BLACK

    def makeEnd(self):
        self.color = GREEN

    def makePath(self):
        self.color = YELLOW

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def updateNeighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].isBarrier():  # Moving DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].isBarrier():  # Moving UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].isBarrier():  # Moving RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].isBarrier():  # Moving LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):  # comparing two spots
        return False


def h(p1, p2):  # Heuristic Function
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstructPath(cameFrom, current, draw):
    while current in cameFrom:
        current = cameFrom[current]
        current.makePath()
        draw()
    current.makeStart()

def Algorithm(draw, grid, start, end):
    count = 0
    openSet = PriorityQueue()
    openSet.put((0, count, start))
    cameFrom = {}
    gScore = {spot: float("inf") for row in grid for spot in
              row}  # keeps track of the shortest distance between start node to current node
    gScore[start] = 0
    fScore = {spot: float("inf") for row in grid for spot in
              row}  # keeps track of the assumed distance between current node to end node
    fScore[start] = h(start.getPos(), end.getPos())

    openSetHash = {start}  # To keep track of items in Priority Queue

    while not openSet.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = openSet.get()[2]
        openSetHash.remove(current)

        if current == end:
            reconstructPath(cameFrom, end, draw)
            end.makeEnd()
            return True

        for neighbor in current.neighbors:
            tempGScore = gScore[current] + 1

            if tempGScore < gScore[neighbor]:
                cameFrom[neighbor] = current
                gScore[neighbor] = tempGScore
                fScore[neighbor] = tempGScore + h(neighbor.getPos(), end.getPos())
                if neighbor not in openSetHash:
                    count += 1
                    openSet.put((fScore[neighbor], count, neighbor))
                    openSetHash.add(neighbor)
                    neighbor.makeOpen()

        draw()

        if current != start:
            current.makeClosed()

    return False


def makeGrid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def drawGrid(win, rows, width):    # Drawing grid lines
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    drawGrid(win, rows, width)
    pygame.display.update()


def getClickedPos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col


def main(win, width):
    ROWS = 50
    grid = makeGrid(ROWS, width)

    start = None
    end = None

    run = True
    started = False
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue
            # Getting the clicked mouse position
            if pygame.mouse.get_pressed()[0]: # Left Mouse Button
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.makeStart()

                elif not end and spot != start:
                    end = spot
                    end.makeEnd()

                elif spot != end and spot != start:
                    spot.makeBarrier()

            elif pygame.mouse.get_pressed()[2]:  # Right Mouse Button
                pos = pygame.mouse.get_pos()
                row, col = getClickedPos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.updateNeighbors(grid)

                    Algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = makeGrid(ROWS, width)

    pygame.quit()


main(WIN, WIDTH)
