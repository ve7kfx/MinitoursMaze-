import random

# ANSI escape code constants
ANSI_RESET = "\u001B[0m"
ANSI_WHITE = "\u001B[37m"
ANSI_BLACK = "\u001B[30m"
ANSI_CYAN = "\u001B[36m"  # Color for the end of the maze

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [['#' for _ in range(self.width)] for _ in range(self.height)]
        self.generate_maze(1, 1)

    def generate_maze(self, x, y):
        directions = ['N', 'S', 'E', 'W']
        random.shuffle(directions)

        for direction in directions:
            dx, dy = 0, 0
            if direction == 'N':
                dx, dy = 0, -2
            elif direction == 'S':
                dx, dy = 0, 2
            elif direction == 'W':
                dx, dy = -2, 0
            elif direction == 'E':
                dx, dy = 2, 0

            nx, ny = x + dx, y + dy
            if 1 <= nx < self.width - 1 and 1 <= ny < self.height - 1 and self.grid[ny][nx] == '#':
                self.grid[ny][nx] = ' '
                self.grid[ny - dy // 2][nx - dx // 2] = ' '
                self.generate_maze(nx, ny)

    def display_maze(self, player, minitaurs, arrows):
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) == (self.width - 2, self.height - 2):
                    print(ANSI_CYAN + '!' + ANSI_RESET, end='')  # Exit in cyan
                elif (x, y) == player.position:
                    print(player.symbol, end='')  # Player
                elif any(minitaur.position == (x, y) for minitaur in minitaurs):
                    print('x', end='')  # Minitaurs
                elif any(arrow.position == (x, y) for arrow in arrows):
                    print('>', end='')  # Arrows
                elif self.grid[y][x] == '#':
                    print(ANSI_WHITE + '#' + ANSI_RESET, end='')  # Walls in white
                else:
                    print(ANSI_BLACK + ':' + ANSI_RESET, end='')  # Paths in black
            print()

class GameEntity:
    def __init__(self, symbol, position):
        self.symbol = symbol
        self.position = position

class Player(GameEntity):
    def __init__(self, position):
        super().__init__('*', position)
        self.arrows = 0

class Minitaur(GameEntity):
    def __init__(self, position):
        super().__init__('x', position)

class Arrow(GameEntity):
    def __init__(self, position):
        super().__init__('>', position)

class MazeGame:
    def __init__(self, width, height, num_minitaurs):
        self.maze = Maze(width, height)
        self.player = Player((1, 1))
        self.minitaurs = [Minitaur(self.get_random_position()) for _ in range(num_minitaurs)]
        self.arrows = [Arrow(self.get_random_position()) for _ in range(3)]
        self.game_over = False

    def get_random_position(self):
        while True:
            x = random.randint(1, self.maze.width - 2)
            y = random.randint(1, self.maze.height - 2)
            if self.maze.grid[y][x] == ' ':
                return x, y

    def start(self):
        while not self.game_over:
            self.maze.display_maze(self.player, self.minitaurs, self.arrows)
            self.handle_player_input()
            self.update_game_state()

    def handle_player_input(self):
        command = input("Enter command (WASD to move, IJKL to shoot, Q to quit): ").lower()
        if command == 'q':
            self.game_over = True
            print("You quit the game.")
            return
        if command in ['w', 'a', 's', 'd']:
            self.move_player(command)
        elif command in ['i', 'j', 'k', 'l'] and self.player.arrows > 0:
            self.shoot_arrow(command)

    def move_player(self, direction):
        dx, dy = 0, 0
        if direction == 'w':
            dy = -1
        elif direction == 's':
            dy = 1
        elif direction == 'a':
            dx = -1
        elif direction == 'd':
            dx = 1
        new_x = self.player.position[0] + dx
        new_y = self.player.position[1] + dy
        if 0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height and self.maze.grid[new_y][new_x] == ' ':
            self.player.position = (new_x, new_y)

    def shoot_arrow(self, direction):
        dx, dy = 0, 0
        if direction == 'i':
            dy = -1
        elif direction == 'k':
            dy = 1
        elif direction == 'j':
            dx = -1
        elif direction == 'l':
            dx = 1
        arrow_x, arrow_y = self.player.position
        while True:
            arrow_x += dx
            arrow_y += dy
            if not (0 <= arrow_x < self.maze.width and 0 <= arrow_y < self.maze.height) or self.maze.grid[arrow_y][arrow_x] == '#':
                break
            hit_minitaur = next((m for m in self.minitaurs if m.position == (arrow_x, arrow_y)), None)
            if hit_minitaur:
                self.minitaurs.remove(hit_minitaur)
                print("You hit a minitaur!")
                break
        self.player.arrows -= 1

    def collect_arrow(self):
        for arrow in self.arrows:
            if arrow.position == self.player.position:
                self.player.arrows += 1
                self.arrows.remove(arrow)
                print("You collected an arrow! Total arrows:", self.player.arrows)

    def update_game_state(self):
        self.collect_arrow()
        for minitaur in self.minitaurs:
            self.move_minitaur(minitaur)
            if minitaur.position == self.player.position:
                self.game_over = True
                print("Game Over! You were caught by a minitaur.")
                return
        if self.player.position == (self.maze.width - 2, self.maze.height - 2):
            self.game_over = True
            print("Congratulations! You have escaped the maze.")

    def move_minitaur(self, minitaur):
        directions = ['w', 'a', 's', 'd']
        direction = random.choice(directions)
        dx, dy = 0, 0
        if direction == 'w':
            dy = -1
        elif direction == 's':
            dy = 1
        elif direction == 'a':
            dx = -1
        elif direction == 'd':
            dx = 1
        new_x = minitaur.position[0] + dx
        new_y = minitaur.position[1] + dy
        if 0 <= new_x < self.maze.width and 0 <= new_y < self.maze.height and self.maze.grid[new_y][new_x] == ' ':
            minitaur.position = (new_x, new_y)

if __name__ == "__main__":
    width = 80
    height = 20
    num_minitaurs = int(input("Enter the number of minitaurs (0-12): "))
    game = MazeGame(width, height, num_minitaurs)
    game.start()
